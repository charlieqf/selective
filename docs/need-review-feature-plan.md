# Need Review Feature - Implementation Plan

## Goal

Implement a "Need Review" marking system that allows users to:
1. Manually set/unset "Need Review" status on any question
2. Auto-mark as "Need Review" when answering incorrectly (already implemented)
3. View Need Review count for each Collection
4. Quick-access to filtered Need Review list per Collection

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Authorization | Author-only | Single-user model, no collaborators |
| Status Transitions | Unrestricted | Allow any status change for flexibility |
| Filtering | Use existing `GET /items?status=` | No need for dedicated endpoint |
| Canonical Statuses | `UNANSWERED`, `ANSWERED`, `MASTERED`, `NEED_REVIEW` | Already enforced by DB CHECK constraint |
| Ownership Predicate | `Item.author_id` | Items belong to author, not collection owner |
| Toggle Restore Logic | Restore to `ANSWERED` if attempts > 0, else `UNANSWERED` | Infer from existing data |

## Known Limitations

1. **Collection counts only include author's items**: The aggregation filters by `Item.author_id == current_user_id`. If items were imported/seeded with different authors, they won't be counted. This is by design for the single-user model.

2. **Toggle restore is inferred**: When unmarking NEED_REVIEW, status is restored to ANSWERED (if item has attempts) or UNANSWERED (if never attempted). Original MASTERED status is not preserved without database migration.

---

## Proposed Changes

### Backend

#### [MODIFY] [items.py](file:///c:/work/me/selective/backend/app/routes/items.py)

Add manual status toggle API with proper validation:

```python
@bp.route('/<int:id>/status', methods=['PATCH'])
@jwt_required()
def update_item_status(id):
    """Manually toggle item status (for Need Review marking)"""
    current_user_id = get_jwt_identity()
    
    # Return 404 for non-owned items (hides existence)
    item = Item.query.filter_by(id=id, author_id=current_user_id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    # Validate request body exists and has content-type
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Request body required'}), 400
    if 'status' not in data:
        return jsonify({'error': 'status field is required'}), 400
    
    new_status = data.get('status')
    # Match DB CHECK constraint exactly
    allowed_statuses = ['UNANSWERED', 'ANSWERED', 'MASTERED', 'NEED_REVIEW']
    if new_status not in allowed_statuses:
        return jsonify({'error': f'Invalid status. Allowed: {allowed_statuses}'}), 400
    
    item.status = new_status
    db.session.commit()
    
    return jsonify({'status': item.status, 'id': item.id}), 200
```

---

#### [MODIFY] [collections.py](file:///c:/work/me/selective/backend/app/routes/collections.py)

Optimize `get_collections()` using aggregated count (ownership via `author_id`):

```python
from sqlalchemy import func, case

@bp.route('', methods=['GET'])
@jwt_required()
def get_collections():
    current_user_id = get_jwt_identity()
    
    # Subquery: count items by collection where author matches current user
    # This ensures we only count items the user owns, matching single-user model
    item_counts = db.session.query(
        Item.collection_id,
        func.count(Item.id).label('total_count'),
        func.sum(case((Item.status == 'NEED_REVIEW', 1), else_=0)).label('need_review_count')
    ).filter(
        Item.author_id == current_user_id
    ).group_by(Item.collection_id).subquery()
    
    # Join collections with counts
    collections = db.session.query(
        Collection, 
        func.coalesce(item_counts.c.total_count, 0).label('total_count'),
        func.coalesce(item_counts.c.need_review_count, 0).label('need_review_count')
    ).outerjoin(
        item_counts, Collection.id == item_counts.c.collection_id
    ).filter(
        Collection.user_id == current_user_id,
        Collection.is_deleted == False
    ).order_by(Collection.created_at.desc()).all()
    
    result = []
    for c, total, need_review in collections:
        data = c.to_dict()
        data['total_count'] = total
        data['need_review_count'] = need_review
        result.append(data)
    
    return jsonify(result), 200
```

---

#### [NEW] [test_item_status.py](file:///c:/work/me/selective/backend/tests/test_item_status.py)

Backend tests with proper fixtures:

```python
import pytest

@pytest.fixture
def test_item(client, auth_headers):
    """Create a test item owned by the authenticated user"""
    response = client.post('/api/items', json={
        'title': 'Test Question',
        'difficulty': 3
    }, headers=auth_headers)
    return response.json

def test_update_status_success(client, auth_headers, test_item):
    """Happy path: author can change status to any valid value"""
    for status in ['NEED_REVIEW', 'ANSWERED', 'MASTERED', 'UNANSWERED']:
        response = client.patch(f'/api/items/{test_item["id"]}/status', 
            json={'status': status}, headers=auth_headers)
        assert response.status_code == 200
        assert response.json['status'] == status

def test_update_status_invalid_status(client, auth_headers, test_item):
    """Invalid status value returns 400"""
    response = client.patch(f'/api/items/{test_item["id"]}/status', 
        json={'status': 'INVALID'}, headers=auth_headers)
    assert response.status_code == 400
    assert 'Invalid status' in response.json['error']

def test_update_status_missing_body(client, auth_headers, test_item):
    """Missing request body returns 400"""
    response = client.patch(f'/api/items/{test_item["id"]}/status', 
        headers=auth_headers, content_type='application/json')
    assert response.status_code == 400

def test_update_status_empty_body(client, auth_headers, test_item):
    """Empty JSON body returns 400"""
    response = client.patch(f'/api/items/{test_item["id"]}/status', 
        json={}, headers=auth_headers)
    assert response.status_code == 400
    assert 'status field is required' in response.json['error']

def test_update_status_not_owner(client, other_user_headers, test_item):
    """Non-owner gets 404 (not 403 to hide existence)"""
    response = client.patch(f'/api/items/{test_item["id"]}/status', 
        json={'status': 'NEED_REVIEW'}, headers=other_user_headers)
    assert response.status_code == 404

def test_update_status_nonexistent(client, auth_headers):
    """Non-existent item returns 404"""
    response = client.patch('/api/items/99999/status', 
        json={'status': 'NEED_REVIEW'}, headers=auth_headers)
    assert response.status_code == 404
```

#### [NEW] [test_collections_counts.py](file:///c:/work/me/selective/backend/tests/test_collections_counts.py)

Test aggregated counts:

```python
def test_collection_need_review_count(client, auth_headers):
    """Verify need_review_count is returned and accurate"""
    # Create collection
    col = client.post('/api/collections', json={'name': 'Math'}, headers=auth_headers).json
    
    # Create items with different statuses
    client.post('/api/items', json={'collection_id': col['id'], 'status': 'NEED_REVIEW'}, headers=auth_headers)
    client.post('/api/items', json={'collection_id': col['id'], 'status': 'NEED_REVIEW'}, headers=auth_headers)
    client.post('/api/items', json={'collection_id': col['id'], 'status': 'MASTERED'}, headers=auth_headers)
    
    # Fetch collections
    response = client.get('/api/collections', headers=auth_headers)
    assert response.status_code == 200
    
    math_col = next(c for c in response.json if c['name'] == 'Math')
    assert math_col['need_review_count'] == 2
    assert math_col['total_count'] == 3
```

---

### Frontend

#### [MODIFY] [QuestionDetail.vue](file:///c:/work/me/selective/frontend/src/views/questions/QuestionDetail.vue)

Add "Mark for Review" toggle button:

```vue
<!-- Add in header area -->
<n-button 
  v-if="canEdit"
  :type="item.status === 'NEED_REVIEW' ? 'warning' : 'default'"
  @click="toggleNeedReview"
>
  {{ item.status === 'NEED_REVIEW' ? 'Remove Review Mark' : 'Mark for Review' }}
</n-button>
```

```javascript
async function toggleNeedReview() {
  const newStatus = item.value.status === 'NEED_REVIEW' ? 'UNANSWERED' : 'NEED_REVIEW'
  try {
    await itemsApi.updateStatus(item.value.id, newStatus)
    item.value.status = newStatus
    message.success(newStatus === 'NEED_REVIEW' ? 'Marked for review' : 'Review mark removed')
  } catch (error) {
    message.error('Operation failed')
  }
}
```

---

#### [MODIFY] [items.js](file:///c:/work/me/selective/frontend/src/api/items.js)

Add API call:

```javascript
updateStatus(id, status) {
  return api.patch(`/items/${id}/status`, { status })
}
```

---

#### [MODIFY] [DashboardView.vue](file:///c:/work/me/selective/frontend/src/views/dashboard/DashboardView.vue)

Show Need Review count and quick access per Collection:

```vue
<n-grid-item v-for="collection in collections" :key="collection.id">
  <n-card :title="collection.name">
    <n-space vertical>
      <div>Total: {{ collection.total_count }}</div>
      <div>Need Review: {{ collection.need_review_count }}</div>
    </n-space>
    <template #action>
      <n-button 
        v-if="collection.need_review_count > 0"
        size="small" 
        type="warning"
        @click="goToReview(collection.id)"
      >
        Review ({{ collection.need_review_count }})
      </n-button>
    </template>
  </n-card>
</n-grid-item>
```

```javascript
function goToReview(collectionId) {
  router.push({
    path: '/questions',
    query: { collection_id: collectionId, status: 'NEED_REVIEW' }
  })
}
```

---

## Verification Plan

### Automated Tests
```bash
cd backend && python -m pytest tests/test_item_status.py tests/test_collections_counts.py -v
```

### Manual Verification
1. **Manual Marking Test**:
   - Open any question -> Click "Mark for Review" -> Verify status changes
   - Click "Remove Review Mark" -> Verify status reverts

2. **Collection Count Test**:
   - View Dashboard -> Check Need Review counts per subject
   - Click "Review (N)" button -> Verify redirect to filtered list

3. **End-to-End Loop Test**:
   - Upload question -> Answer wrong -> Verify auto-marked as Need Review
   - Answer correct -> Verify status becomes Mastered
