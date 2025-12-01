# Mobile Camera Capture - Implementation Plan

## Goal

Enable students to directly capture question photos using their mobile device camera, eliminating the need to first save photos to gallery.

## Proposed Changes

### Frontend Components

#### [MODIFY] [ImageUploader.vue](file:///c:/work/me/selective/frontend/src/components/ImageUploader.vue)

Add camera capture functionality:
- Add `capture="environment"` attribute to file input for rear camera
- Detect mobile device and show camera icon
- Implement preview modal before upload
- Add error handling for camera permissions

**Key Implementation**:
```vue
<!-- Two upload options -->
<input 
  type="file" 
  accept="image/*" 
  capture="environment"  <!-- Use rear camera on mobile -->
  @change="handleCameraCapture"
  style="display: none"
  ref="cameraInput"
/>
<input 
  type="file" 
  accept="image/*"
  @change="handleFileSelect"  <!-- Gallery selection -->
  style="display: none"
  ref="fileInput"
/>

<!-- Mobile-friendly buttons -->
<n-button @click="$refs.cameraInput.click()" v-if="isMobile">
  <template #icon><n-icon><CameraIcon /></template>
  拍照
</n-button>
<n-button @click="$refs.fileInput.click()">
  <template #icon><n-icon><ImageIcon /></template>
  {{ isMobile ? '相册' : '选择图片' }}
</n-button>

<!-- Preview Modal with Manual Rotation -->
<n-modal v-model:show="showPreview">
  <img :src="previewUrl" :style="{ transform: `rotate(${rotation}deg)` }" />
  <n-space>
    <n-button @click="rotation -= 90">↶ 左转</n-button>
    <n-button @click="rotation += 90">↷ 右转</n-button>
    <n-button type="primary" @click="confirmUpload">确认上传</n-button>
  </n-space>
</n-modal>
```

#### [MODIFY] [QuestionUpload.vue](file:///c:/work/me/selective/frontend/src/views/questions/QuestionUpload.vue)

Update mobile hints:
- Add instruction text: "拍照上传题目图片"
- Emphasize camera-first workflow on mobile
- Ensure responsive layout for camera preview

---

### User Experience Flow

**Mobile Device (Primary)**:
1. Student opens upload page
2. Sees prominent "拍照" button
3. Taps → Camera opens directly
4. Takes photo → Preview shown
5. Confirm → Upload to Cloudinary
6. Can take multiple photos in sequence

**Desktop (Fallback)**:
1. Standard file selection dialog
2. Choose from file system

**Permission Denied Flow**:
1. User taps "拍照" → Browser shows permission dialog
2. User selects "Don't Allow"
3. System shows error toast: "需要摄像头权限才能拍照，请使用相册上传"
4. Automatically switch to gallery mode (file input)
5. Log permission denial for analytics

---

---

### Image Orientation Handling

**Problem**: Photos taken at different angles (portrait/landscape) need to display correctly regardless of device orientation.

**Solution**: Cloudinary auto-orientation with client-side fallback

**Implementation**:

1. **Primary**: Cloudinary server-side rotation
   ```javascript
   // In uploadApi.uploadImage()
   const transformation = {
     flags: 'progressive',
     quality: 'auto',
     fetch_format: 'auto',
     angle: 'exif'  // Auto-rotate based on EXIF
   }
   ```

2. **Fallback**: Client-side rotation when EXIF is stripped (iOS Safari Live photos)
   ```javascript
   // In ImageUploader.vue - before upload
   async function detectAndFixOrientation(file) {
     // Try to read EXIF
     const orientation = await getExifOrientation(file)
     
     if (orientation && orientation !== 1) {
       // EXIF present, Cloudinary will handle it
       return file
     }
     
     // EXIF missing or stripped - use Canvas to detect & fix
     return await rotateImageIfNeeded(file)
   }
   
   async function rotateImageIfNeeded(file) {
     const img = await loadImage(file)
     
     // Heuristic: if width < height, likely needs rotation
     // (Student typically holds phone vertically)
     if (img.width < img.height) {
       return file  // Already portrait, no rotation needed
     }
     
     // Rotate 90° clockwise using Canvas
     const canvas = document.createElement('canvas')
     canvas.width = img.height
     canvas.height = img.width
     const ctx = canvas.getContext('2d')
     ctx.translate(canvas.width / 2, canvas.height / 2)
     ctx.rotate(90 * Math.PI / 180)
     ctx.drawImage(img, -img.width / 2, -img.height / 2)
     
     return new Promise(resolve => {
       canvas.toBlob(resolve, file.type, 0.95)
     })
   }
   ```

**How it works**:
- **Step 1**: Show preview modal immediately after photo capture
- **Step 2**: Auto-rotate based on EXIF (if present) or aspect ratio (fallback)
- **Step 3**: User can manually rotate using ↶/↷ buttons if needed
- **Step 4**: On confirm, apply rotation and upload to Cloudinary

**Handling Edge Cases**:
- Wide diagrams (intentional landscape): User rotates manually in preview
- EXIF stripped by browser before compression: Fallback to aspect ratio + manual correction
- Multiple browsers/devices: Preview modal ensures correctness regardless of automated logic

**User Safety Net**: Manual rotation buttons in preview modal prevent all mis-rotation scenarios

---

### Technical Considerations

**Browser API**:
- `capture="environment"` triggers rear camera on iOS/Android
- Fallback to regular file input on desktop
- Works without additional permissions (user grants via browser dialog)

**Mobile Detection**:
```javascript
const isMobile = computed(() => {
  return /Android|iPhone|iPad|iPod/i.test(navigator.userAgent)
})
```

**Accessibility**:
- Camera button: `aria-label="使用摄像头拍照"`
- Gallery button: `aria-label="从相册选择图片"`
- Both buttons accessible via keyboard (Tab + Enter)
- Preview modal includes close button with `aria-label="关闭预览"`
- Upload progress announced to screen readers

**Image Compression**:
**Decision**: Implement client-side compression using `browser-image-compression`

**Rationale**:
- Mobile photos average 4-8MB, too large for quick uploads
- Cloudinary has upload limits
- Better UX with faster uploads

**Implementation**:
```javascript
import imageCompression from 'browser-image-compression'

async function compressImage(file) {
  const options = {
    maxSizeMB: 2,
    maxWidthOrHeight: 1920,
    useWebWorker: true,
    preserveExif: true  // Keep EXIF for orientation
  }
  
  try {
    return await imageCompression(file, options)
  } catch (error) {
    console.warn('Compression failed, uploading original:', error)
    return file  // Fallback to original
  }
}
```

**Quality Parameters**:
5. Test sequential multi-photo capture

### E2E Tests

**Challenge**: Playwright cannot access real device cameras

**Strategy**: Split tests into two modes with appropriate mocks

#### Test 1: File Selection Mode (Existing)
```javascript
test('should upload via file selection', async ({ page }) => {
  const filePath = path.join(__dirname, 'fixtures', 'test-image.jpg')
  await page.setInputFiles('input[type="file"]:not([capture])', filePath)
  // ... rest of test
})
```

#### Test 2: Camera Capture Mode (New)
```javascript
test('should upload via camera capture', async ({ page }) => {
  await page.goto('/questions/upload')
  
  // Locate camera input (has capture="environment" attribute)
  const cameraInput = page.locator('input[type="file"][capture="environment"]')
  
  // Create mock camera photo from fixture
  const testImagePath = path.join(__dirname, 'fixtures', 'test-image.jpg')
  
  // Inject file into camera input
  await cameraInput.setInputFiles(testImagePath)
  
  // Preview modal should appear
  await expect(page.locator('.n-modal:has-text("确认上传")')).toBeVisible()
  
  // Optional: test manual rotation
  await page.click('button:has-text("↷ 右转")')
  await page.waitForTimeout(100)
  
  // Confirm upload
  await page.click('button:has-text("确认上传")')
  
  // Wait for Cloudinary upload to complete (mocked in beforeEach)
  await expect(page.locator('.n-upload-file-info')).toBeVisible({ timeout: 5000 })
  
  // Verify image appears in preview list
  const uploadedImage = page.locator('img[src*="cloudinary"]').first()
  await expect(uploadedImage).toBeVisible()
  
  // Verify can proceed to form submission
  await page.fill('input[placeholder*="Title"]', 'Camera Test Question')
  await page.click('button:has-text("Upload Question")')
  await expect(page).toHaveURL(/\/questions$/)
})
```

#### Test 3: Permission Denial
```javascript
test('should fallback to gallery on permission denial', async ({ page, context }) => {
  // Mock permission denial
  await context.grantPermissions([], { origin: page.url() })
  
  await page.click('button:has-text("拍照")')
  
  // Should show error toast
  await expect(page.locator('.n-message:has-text("需要摄像头权限")')).toBeVisible()
  
  // Camera input should be disabled/hidden
  // Gallery input should remain available
})
```

**Coverage**:
- ✅ File selection (desktop/fallback mode)
- ✅ Camera capture simulation (mobile mode)
- ✅ Permission denial handling
- ✅ Upload progress and completion

