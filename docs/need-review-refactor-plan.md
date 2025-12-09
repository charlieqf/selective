# Need Review Refactor - Implementation Plan

## Problem

Current model treats `NEED_REVIEW` as a mutually exclusive status alongside `MASTERED/ANSWERED/UNANSWERED`, which forces loss of learning progress when marking/unmarking for review.

## Proposed Solution

Separate "needs review" into an independent boolean flag, keeping status as pure learning state.

## Data Model Changes

### Item Model
```python
# Status remains learning progression only
status = db.Column(db.String(20), default='UNANSWERED')  # UNANSWERED, ANSWERED, MASTERED

# Add separate review flag
needs_review = db.Column(db.Boolean, default=False, nullable=False)
```

### Migration
1. Add `needs_review` column (default False)
2. Backfill: `UPDATE items SET needs_review=TRUE, status='ANSWERED' WHERE status='NEED_REVIEW'`
3. Update CHECK constraint to remove `NEED_REVIEW` from allowed statuses
4. Drop `previous_status` column (no longer needed)

---

## API Changes

### New Endpoint
```
PATCH /api/items/<id>/review
Body: { "needs_review": true/false }
Response: { "needs_review": true/false, "status": "MASTERED" }
```

### Modified Endpoints
- `GET /api/items` - Add `needs_review=true` filter parameter
- `GET /api/collections` - Count `needs_review=True` instead of `status='NEED_REVIEW'`
- `POST /api/items/<id>/answers` - Set `needs_review=True` on wrong answer (not change status)

---

## Frontend Changes

### QuestionDetail.vue
- Toggle button only flips `needs_review` flag
- Show both status tag AND review badge
- Call new `/review` endpoint

### DashboardView.vue  
- Use `needs_review_count` from collections API
- Review button filters by `needs_review=true`

### items.js API
- Add `toggleReview(id, needsReview)` method
- Remove `updateStatusWithRestore`

---

## Files to Modify

| File | Action |
|------|--------|
| `backend/app/models/item.py` | Add `needs_review`, remove `previous_status` |
| `backend/app/routes/items.py` | Add `/review` endpoint, update status logic |
| `backend/app/routes/collections.py` | Count by `needs_review` |
| `backend/app/routes/answer.py` | Set `needs_review=True` on wrong answer |
| `migrations/` | New migration for schema change |
| `frontend/src/api/items.js` | Add `toggleReview` method |
| `frontend/src/views/questions/QuestionDetail.vue` | Update toggle logic |
| `frontend/src/views/dashboard/DashboardView.vue` | Update filter |
| `backend/tests/test_item_status.py` | Update tests |

---

## Benefits

1. ✅ No loss of MASTERED/ANSWERED status when marking for review
2. ✅ Cleaner data model - learning state and review state are independent
3. ✅ Simpler API - no need for `restore_previous` logic
4. ✅ Better UX - can show both "Mastered" badge AND "Needs Review" badge

---

## Questions for User

1. Should we use boolean `needs_review` or timestamp `needs_review_at`? (Timestamp allows tracking when marked)
2. Backfill strategy: Set status to `ANSWERED` for items currently `NEED_REVIEW`?
