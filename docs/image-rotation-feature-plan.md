# Image Rotation Feature - Implementation Plan (Revised)

## Goal

Allow students to rotate question images while browsing/studying and persist the rotation angle so all future views display correctly.

## Key Decisions

### 1. **Per-Image Rotation** (Not Per-Item)
Store rotation in `images` JSON array since items can have multiple photos.

### 2. **Cloudinary SDK** (Not Query Parameters)
Use `@cloudinary/url-gen` for proper transformation URLs.

### 3. **Author-Only Permission**
Only the item's author can rotate images (teachers/parents cannot modify student work).

### 4. **Cache Busting via Timestamp**
Use `item.updated_at` in URL to invalidate cache when rotation changes.

---

## Backend Changes

### Database Schema

**No migration needed** - Store rotation in existing `images` JSON:

```python
# Before
images = [
  {"url": "https://cloudinary.../img1.jpg", "public_id": "abc123"}
]

# After
images = [
  {"url": "https://cloudinary.../img1.jpg", "public_id": "abc123", "rotation": 90}
]
```

**Backward Compatibility**: Existing images without `rotation` default to 0.

### API Endpoint

```python
# backend/app/routes/items.py
from datetime import datetime

@items_bp.route('/<int:id>/rotate', methods=['PATCH'])
@login_required
def rotate_image(id):
    """Update rotation for a specific image"""
    data = request.json
    image_index = data.get('image_index', 0)
   rotation = data.get('rotation', 0)
    
    # Validate
    if rotation not in [0, 90, 180, 270]:
        return {'error': 'Invalid rotation'}, 400
    
    item = Item.query.get_or_404(id)
    
    # Authorization: Author only
    if item.author_id != current_user.id:
        return {'error': 'Unauthorized'}, 403
    
    # Update JSON
    if not item.images or image_index >= len(item.images):
        return {'error': 'Invalid image index'}, 400
    
    images = list(item.images)  # Copy to trigger SQLAlchemy change detection
    if not isinstance(images[image_index], dict):
        images[image_index] = {'url': images[image_index]}
    
    images[image_index]['rotation'] = rotation
    item.images = images
    item.updated_at = datetime.utcnow()  # Cache bust
    
    db.session.commit()
    
    return {
        'rotation': rotation,
        'image_index': image_index,
        'updated_at': item.updated_at.isoformat()
    }
```

---

## Frontend Changes

### Install Cloudinary SDK

```bash
npm install @cloudinary/url-gen
```

### QuestionDetail.vue

```vue
<template>
  <div class="question-detail">
    <div class="image-container" v-for="(image, index) in item.images" :key="index">
      <img :src="getRotatedUrl(image, index)" :alt="`Image ${index + 1}`" />
      
      <!-- Rotation Controls (Keyboard Accessible) -->
      <div class="rotation-controls" role="toolbar" aria-label="图片旋转工具">
        <n-button 
          circle 
          @click="rotate(-90, index)" 
          aria-label="向左旋转90度"
          :tabindex="0"
        >
          <template #icon><n-icon><ArrowRotateLeft /></n-icon></template>
        </n-button>
        <n-button 
          circle 
          @click="rotate(90, index)" 
          aria-label="向右旋转90度"
          :tabindex="0"
        >
          <template #icon><n-icon><ArrowRotateRight /></n-icon></template>
        </n-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Cloudinary } from '@cloudinary/url-gen'
import { rotate } from '@cloudinary/url-gen/actions/rotate'
import { byAngle } from '@cloudinary/url-gen/qualifiers/rotate'
import { autoGravity } from '@cloudinary/url-gen/qualifiers/gravity'
import { auto } from '@cloudinary/url-gen/qualifiers/format'
import { auto as autoQuality } from '@cloudinary/url-gen/qualifiers/quality'

const cloudinary = new Cloudinary({
  cloud: { cloudName: import.meta.env.VITE_CLOUDINARY_CLOUD_NAME }
})

function getRotatedUrl(image, index) {
  if (!image?.public_id) return image?.url || ''
  
  const rotation = image.rotation || 0
  
  // Build proper Cloudinary transformation  const cldImage = cloudinary.image(image.public_id)
  
  if (rotation !== 0) {
    cldImage.rotate(byAngle(rotation))
  }
  
  cldImage
    .format(auto())
    .quality(autoQuality())
    .gravity(autoGravity())
  
  // Cache busting: append item's updated_at
  return `${cldImage.toURL()}?v=${props.item.updated_at}`
}

async function rotate(angle, imageIndex) {
  const images = [...props.item.images]
  const currentRotation = images[imageIndex]?.rotation || 0
  const newRotation = (currentRotation + angle + 360) % 360
  
  // Optimistic update
  images[imageIndex] = { ...images[imageIndex], rotation: newRotation }
  props.item.images = images
  
  try {
    const { data } = await axios.patch(`/api/items/${props.item.id}/rotate`, {
      image_index: imageIndex,
      rotation: newRotation
    })
    
    props.item.updated_at = data.updated_at
    message.success('已旋转')
  } catch (error) {
    // Revert on error
    images[imageIndex].rotation = currentRotation
    props.item.images = images
    message.error('保存失败')
  }
}
</script>

<style scoped>
.rotation-controls {
  position: absolute;
  bottom: 16px;
  right: 16px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  padding: 8px;
  display: flex;
  gap: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

/* Accessibility */
.rotation-controls button {
  min-width: 44px;
  min-height: 44px;  /* WCAG touch target */
}

.rotation-controls button:focus-visible {
  outline: 3px solid var(--primary-color);
  outline-offset: 2px;
}
</style>
```

---

## Cloudinary URL Structure

### ❌ Incorrect (Query Parameter)
```
https://res.cloudinary.com/demo/sample.jpg?a_90
```

### ✅ Correct (Transformation Path)
```
https://res.cloudinary.com/demo/image/upload/a_90/sample.jpg
```

**Cloudinary SDK handles this automatically** via `.toURL()`.

---

## Caching Strategy

1. **Cloudinary**: Caches each transformation (`a_0`, `a_90`, etc.)
2. **Client**: `?v=${updated_at}` invalidates browser cache when rotation changes
3. **CDN**: Cloudinary CDN serves cached transformations globally

**Trade-off**: Creating 4 versions (0°/90°/180°/270°) uses storage, but optimizes delivery.

---

## Concurrency Handling

**Strategy**: Last write wins + Author-only access

```python
# Current approach (acceptable for single-user context)
item.rotation = new_rotation  # Absolute value

# Alternative (optimistic locking - future enhancement)
if item.updated_at != expected_timestamp:
    return {'error': 'Stale data, please refresh'}, 409
```

**Justification**: 
- Students work on their own items (no concurrent edits expected)
- Teachers/parents have read-only access
- Refresh-on-conflict is acceptable UX

---

## Accessibility Checklist

- ✅ `aria-label` on rotation buttons
- ✅ `role="toolbar"` on controls container
- ✅ `tabindex="0"` for keyboard access
- ✅ 44x44px touch targets (WCAG 2.1)
- ✅ `:focus-visible` outline (3px)
- ✅ High contrast background (rgba(255,255,255,0.95))

---

## Migration Plan

### Phase 1: Soft Launch (No DB Migration)
1. Deploy backend API
2. Deploy frontend with Cloudinary SDK
3. Existing items: `rotation` defaults to 0 (no visual change)
4. New rotations: Saved incrementally as users rotate

### Phase 2: Data Cleanup (Optional)
```python
# Script to initialize rotation for all images
for item in Item.query.all():
    if item.images:
        images = list(item.images)
        for img in images:
            if isinstance(img, dict) and 'rotation' not in img:
                img['rotation'] = 0
        item.images = images
db.session.commit()
```

**Not required** - frontend handles missing `rotation` gracefully.

---

## Testing

### Backend
```python
def test_rotate_multiple_images():
    item = create_multi_image_item()
    
    # Rotate second image
    response = client.patch(f'/items/{item.id}/rotate', json={
        'image_index': 1,
        'rotation': 180
    })
    
    assert response.json['rotation'] == 180
    assert item.images[1]['rotation'] == 180
    assert item.images[0].get('rotation', 0) == 0  # First unchanged
```

### Frontend
```javascript
test('should rotate each image independently', async ({ page }) => {
  // Item with 2 images
  await page.goto('/questions/123')
  
  // Rotate first image
  await page.click('[aria-label="向右旋转90度"]').first()
  
  // Verify only first image URL changed
  const img1 = await page.locator('img').first().getAttribute('src')
  expect(img1).toContain('/a_90/')
  
  const img2 = await page.locator('img').nth(1).getAttribute('src')
  expect(img2).not.toContain('/a_90/')
})
```

---

## Summary

| Concern | Solution |
|---------|----------|
| **Multi-image** | Store rotation in `images` JSON per image |
| **Cloudinary URL** | Use `@cloudinary/url-gen` SDK |
| **Caching** | `?v=${updated_at}` + Cloudinary CDN |
| **Concurrency** | Author-only + last-write-wins |
| **Accessibility** | ARIA labels, keyboard nav, 44px targets |
| **Migration** | Zero-downtime (graceful defaults) |
