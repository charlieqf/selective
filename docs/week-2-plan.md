# Implementation Plan - Week 2: Question Management

## Goal Description
Implement the core Question Management features for the NSW Selective Exam Prep platform. This includes the backend API for creating, retrieving, updating, and deleting questions, as well as the frontend views for listing and uploading questions. This corresponds to "Week 2" of the development plan.

## User Review Required
> [!IMPORTANT]
> Please ensure you have the Cloudinary credentials ready, as they are required for image upload.

> [!WARNING]
> **Security & Validation Updates**:
> - **Ownership**: Users can only edit/delete their own questions.
> - **Uploads**: Restricted to images (jpg, png, webp), max 5MB, max 5 images per question.
> - **Validation**: Strict schema validation for subjects (must be in Config.SUBJECTS) and difficulty (1-5).
> - **Auth**: All routes require JWT authentication.
> - **Cleanup**: Images are deleted from Cloudinary when a question is deleted. Frontend attempts to delete uploaded images if question creation is cancelled or fails.
> - **Config**: Frontend uses `VITE_API_URL` for production API connection.
> - **Schema Change**: `image_urls` field renamed to `images` to store objects `{url, public_id}`.

## Proposed Changes

### Backend
#### [NEW] [questions.py](file:///c:/work/me/selective/backend/app/routes/questions.py)
- Implement Blueprint `questions`
- `GET /api/questions`: List questions with pagination and filtering (subject, difficulty, status)
- `POST /api/questions`: Create a new question
    - **Validation**: Validate subject, difficulty, status, `images` count.
- `GET /api/questions/<id>`: Get question details
- `PATCH /api/questions/<id>`: Update question details
    - **Security**: Verify `current_user.id == question.author_id`.
- `DELETE /api/questions/<id>`: Delete a question
    - **Security**: Verify `current_user.id == question.author_id`.
    - **Cleanup**: Delete associated images from Cloudinary using stored `public_id`.

#### [NEW] [upload.py](file:///c:/work/me/selective/backend/app/routes/upload.py)
- Implement Blueprint `upload`
- `POST /api/upload`: Upload image to Cloudinary and return URL + public_id
    - **Security**: Require `@jwt_required`.
    - **Validation**: Check file type (allowed: jpg, png, webp) and size (max 5MB).
    - **Response**: `{"url": "...", "public_id": "..."}`
- `DELETE /api/upload`: Delete image from Cloudinary (by public_id)
    - **Security**: Require `@jwt_required`.
    - **Usage**: Used by frontend to clean up if question creation fails/cancels.

#### [MODIFY] [__init__.py](file:///c:/work/me/selective/backend/app/__init__.py)
- Register `questions` and `upload` blueprints

#### [MODIFY] [question.py](file:///c:/work/me/selective/backend/app/models/question.py)
- **Schema Change**: Rename `image_urls` to `images`.
- **Type**: JSON column storing list of objects: `[{"url": "...", "public_id": "..."}]`.
- **Migration**: Generate migration to rename column.

#### [NEW] [question.py](file:///c:/work/me/selective/backend/app/schemas/question.py)
- Create Marshmallow schema for Question model validation and serialization
- **Constraints**:
    - `subject`: Must be one of `Config.SUBJECTS` keys.
    - `difficulty`: Integer 1-5.
    - `status`: One of `['UNANSWERED', 'ANSWERED', 'MASTERED', 'NEED_REVIEW']`.
    - `images`: List of objects `{'url': str, 'public_id': str}`, max 5 items.

### Frontend
#### [MODIFY] [client.js](file:///c:/work/me/selective/frontend/src/api/client.js)
- Update `baseURL` to use `import.meta.env.VITE_API_URL || '/api'`.

#### [NEW] [questions.js](file:///c:/work/me/selective/frontend/src/api/questions.js)
- API client methods for questions

#### [NEW] [upload.js](file:///c:/work/me/selective/frontend/src/api/upload.js)
- API client methods for upload
- **Cleanup**: Implement `deleteImage` method using `public_id`.

#### [NEW] [question.js](file:///c:/work/me/selective/frontend/src/stores/question.js)
- Pinia store for managing question state
- **State**: `questions`, `currentQuestion`, `loading`, `error`, `pagination` (page, total, per_page).
- **Actions**: `fetchQuestions` (handle pagination/filters), `createQuestion`, `updateQuestion`, `deleteQuestion`.

#### [NEW] [QuestionList.vue](file:///c:/work/me/selective/frontend/src/views/questions/QuestionList.vue)
- Page to display list of questions
- Filter controls (Subject, Difficulty)
- Pagination controls
- **Display**: Render images from `question.images` array.

#### [NEW] [QuestionUpload.vue](file:///c:/work/me/selective/frontend/src/views/questions/QuestionUpload.vue)
- Page to upload new questions
- Image upload integration
- Form for subject, difficulty, etc.
- **Validation**: Frontend validation matching backend rules.
- **Cleanup**: Call `deleteImage` if user cancels or submission fails.

#### [MODIFY] [router/index.js](file:///c:/work/me/selective/frontend/src/router/index.js)
- Add routes for `/questions` and `/questions/upload`
- **Security**: Add `meta: { requiresAuth: true }` to all question routes.

#### [MODIFY] [.env.example](file:///c:/work/me/selective/frontend/.env.example)
- Add `VITE_API_URL` documentation.

## Verification Plan

### Automated Tests
- **Backend API Tests**:
    - Run `pytest` (need to create test files for questions)
    - **Auth**: Test accessing endpoints without token (401).
    - **Ownership**: Test updating another user's question (403).
    - **Validation**: Test invalid subject/difficulty (400).
    - **Upload**: Mock `cloudinary.uploader.upload` to test success/failure.
    - **Cleanup**: Verify `cloudinary.uploader.destroy` is called on question delete using `public_id`.
    - **Upload Delete**: Test `DELETE /api/upload` with valid/invalid public_id and auth.
- **Frontend Tests**:
    - Test `QuestionList` renders questions from store.
    - Test `QuestionUpload` form validation.

### Manual Verification
- **Frontend Walkthrough**:
    1.  Login to the application.
    2.  Navigate to "Upload Question".
    3.  Upload an image and fill in details.
    4.  Submit and verify redirection to list.
    5.  Check "Question List" to see the new question.
    6.  Filter by subject and verify results.
    7.  Try to access `/questions/upload` without login (should redirect).
    8.  **Cleanup**: Delete a question and verify images are removed (check Cloudinary dashboard or logs).
    9.  **Config**: Verify `VITE_API_URL` is respected in network requests.
    10. **Upload Cancel**: Upload an image, then cancel creation. Verify `DELETE /api/upload` is called.
