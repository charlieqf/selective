# Implementation Plan - Week 5: The Learning Loop (Edit, Answer, Review)

## Goal Description

**Week 5 核心目标**：闭环学习流程。
从单纯的"题目管理"进化到"题目练习"。实现**编辑**、**答题**和**错题复习**功能。
- [ ] Create `Answer` model & migration.
- [ ] Implement `POST /answers` logic (status updates).
- [ ] Implement `GET /review-session` logic.
- [ ] Test APIs with Postman.

### Day 3: Question Editing
- [ ] Refactor `QuestionUpload.vue` to support "Edit Mode" (accept `id` prop).
- [ ] Add "Edit" button to QuestionDetail.
- [ ] Verify image updates work correctly.

### Day 4-5: Answering UI
- [ ] Implement `AnswerSection` component.
- [ ] Integrate into `QuestionDetail`.
- [ ] Add "History" tab to see past attempts.

### Day 6: Review Mode [POSTPONED]
- [ ] Create `ReviewSessionView`.
- [ ] Implement "Start Review" button on Dashboard (only if `need_review_count > 0`).
- [ ] Implement session summary (e.g., "You mastered 3 questions today!").

### Day 7: Polish & Testing
- [ ] Verify "Learning Loop": Upload -> Answer Wrong -> Review -> Answer Right -> Mastered.
- [ ] Mobile responsiveness check.

---

## Verification Plan

### Manual Verification
1.  **The Loop Test**:
    - Upload a new question.
    - Go to Detail -> Mark as "Incorrect".
    - Verify Status = "Need Review".
    - Go to Dashboard -> Click "Review (1)".
    - In Review Session -> Mark as "Correct".
    - Verify Status = "Mastered".
    - Verify Review button is disabled/hidden.

2.  **Edit Test**:
    - Edit a question's difficulty.
    - Verify it updates in the list immediately.

---

## Success Criteria
1.  ✅ 完整的闭环：从不懂(Need Review)到懂(Mastered)的流程跑通。
2.  ✅ 错题本功能可用（Review Session）。
3.  ✅ 数据统计准确（Attempts/Success Rate）。
