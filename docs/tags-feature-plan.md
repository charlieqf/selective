# Tags Feature Implementation Plan

## Goal Description
Add support for tagging items (questions) to allow flexible categorization and filtering. Users can assign multiple tags to an item (e.g., 'patterns', 'fractions') and filter items by clicking on these tags within a collection context.

## User Review Required
> [!IMPORTANT]
> **Database Design Choice**: We will use a dedicated `Tag` entity and a many-to-many relationship (`item_tags`) instead of a simple JSON array. This allows for:
> 1. Efficient filtering (finding all items with tag 'X').
> 2. Tag management (renaming tags updates all items).
> 3. Autocomplete support (fetching all existing tags).

> [!NOTE]
> **Scope**: Tags will be scoped to the **User**. A tag 'Math' created by User A is distinct from 'Math' created by User B.

## Detailed Design Decisions

### 1. Tag Uniqueness & Casing
- **Storage**: Tags will be stored with original casing (e.g., "Maths") to respect user preference.
- **Uniqueness**: Enforced **case-insensitively**. "maths" and "Maths" are considered the same tag.
- **Constraint**: Database unique index on `(user_id, LOWER(name))`.
- **API**: When creating a tag, check for existing case-insensitive match. If found, return existing tag.

### 2. Lifecycle & Cleanup
- **Orphaned Tags**: Tags **remain** in the system even if no items use them. This preserves the user's controlled vocabulary for future items and autocomplete.
- **Deletion**: Users can explicitly delete tags via a future Tag Management UI (out of scope for now).

### 3. Filtering Semantics
- **Query Param**: `GET /api/items?tag=A&tag=B`
- **Logic**: **AND**. Items must have *all* specified tags.
- **Implementation**:
    ```python
    tags = request.args.getlist('tag')
    for tag_name in tags:
        query = query.filter(Item.tags.any(func.lower(Tag.name) == tag_name.lower()))
    ```
- **Future**: OR logic is deferred. UI will strictly support "narrowing down" results.

### 4. Performance
- **Indexes**:
    - `tags(user_id, LOWER(name))` for fast lookup/creation.
    - `item_tags(tag_id, item_id)` for fast filtering.
    - `item_tags(item_id, tag_id)` (PK) for fast loading.

### 5. Migration
- **Strategy**: Start empty. No automatic backfill from notes or other fields. Users will tag items progressively.

### 6. Frontend UX
- **Input**: `n-select` with `filterable`, `tag` mode, and `allow-create`.
- **Validation**:
    - Max length: 30 characters.
    - Whitespace: Trimmed automatically.
    - Empty strings: Rejected.
- **Filtering UI**:
    - Active filters shown as closable chips above the list.
    - Clicking a chip removes that specific tag filter.
    - "Clear All" button available if multiple filters active.

## Proposed Changes

### Database Schema

#### [NEW] `Tag` Model
- `id`: Integer (PK)
- `user_id`: Integer (FK to Users)
- `name`: String (Original case)
- `created_at`: DateTime
- **Index**: `idx_tags_user_name_lower` on `(user_id, func.lower(name))` (Unique)

#### [NEW] `item_tags` Association Table
- `item_id`: Integer (FK to Items)
- `tag_id`: Integer (FK to Tags)
- Primary Key: (`item_id`, `tag_id`)
- **Index**: `idx_item_tags_tag_item` on (`tag_id`, `item_id`)

### Backend

#### [MODIFY] [app/models/item.py](file:///c:/work/me/selective/backend/app/models/item.py)
- Add `tags` relationship (many-to-many).

#### [NEW] [app/models/tag.py](file:///c:/work/me/selective/backend/app/models/tag.py)
- Define `Tag` model with case-insensitive unique constraint.

#### [MODIFY] [app/routes/items.py](file:///c:/work/me/selective/backend/app/routes/items.py)
- `POST /api/items`: Accept `tags` list (strings).
    - **Validation**: Enforce max length (30), non-empty, trim whitespace. Return 400 if invalid.
    - Logic: For each valid tag string:
        1. Check DB for case-insensitive match for user.
        2. If exists, use ID. If not, create new.
- `GET /api/items`: Support multiple `tag` params.
    - Implementation: Loop through tags and apply `filter(Item.tags.any(...))` for each to enforce AND.

#### [NEW] [app/routes/tags.py](file:///c:/work/me/selective/backend/app/routes/tags.py)
- `GET /api/tags`: List all tags for the user.
    - **Note**: Returns all tags (expected < 1000 per user). No pagination initially.
    - Optional: `?search=prefix` for future optimization.

### Frontend

#### [MODIFY] [src/views/questions/QuestionUpload.vue](file:///c:/work/me/selective/frontend/src/views/questions/QuestionUpload.vue)
- Add `n-select` (mode="tags") to allow users to input tags.
- Fetch existing tags for autocomplete.

#### [MODIFY] [src/components/QuestionCard.vue](file:///c:/work/me/selective/frontend/src/components/QuestionCard.vue)
- Display tags as clickable chips/badges under the item.
- Clicking a tag navigates to `QuestionList` with `?tag=TagName`.

#### [MODIFY] [src/views/questions/QuestionList.vue](file:///c:/work/me/selective/frontend/src/views/questions/QuestionList.vue)
- Handle `tag` query parameter.
- Pass `tag` filter to API.
- Show active tag filter in UI (allow clearing).

## Verification Plan

### Automated Tests
- **Backend**:
    - Test creating item with new tags.
    - Test creating item with existing tags (reuse).
    - Test filtering items by tag.
    - Test tag isolation between users.
- **Frontend**:
    - Test adding tags in upload form.
    - Test tag display on card.
    - Test clicking tag filters the list.

### Manual Verification
1. Create a question with tags "A", "B".
2. Create another question with tags "B", "C".
3. Filter by "B" -> Should see both.
4. Filter by "A" -> Should see first only.
