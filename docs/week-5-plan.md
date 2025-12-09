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

### Day 6: Need Review 功能
- [ ] **手动标记**：用户可在 QuestionDetail 页面手动设置/取消 "Need Review" 状态
- [ ] **自动标记**：答题错误时自动设置 Need Review（已实现）
- [ ] **Collection 计数**：每个 Collection 显示 Need Review 数量
- [ ] **快捷入口**：每个 Collection 卡片可一键进入该科目的 Need Review 题目列表

### Day 7: Polish & Testing
- [ ] Verify "Learning Loop": Upload -> Answer Wrong -> Need Review -> Answer Right -> Mastered.
- [ ] 手动标记/取消 Need Review 测试
- [ ] Mobile responsiveness check.

---

## Verification Plan

### Manual Verification
1.  **自动标记测试**:
    - 上传新题目 → 答错 → 验证 Status = "Need Review"
    - 再次进入该题 → 答对 → 验证 Status = "Mastered"

2.  **手动标记测试**:
    - 在 QuestionDetail 页面点击 "标记复习" 按钮
    - 验证状态变为 "Need Review"
    - 点击 "取消标记" 按钮
    - 验证状态恢复

3.  **Collection Need Review 计数测试**:
    - 在 Dashboard 或 Collection 列表中查看各科目的 Need Review 数量
    - 点击某科目的 "复习" 快捷入口
    - 验证跳转到该科目的题目列表，且已筛选 status=NEED_REVIEW

---

## Success Criteria
1.  ✅ 完整的闭环：从不懂(Need Review)到懂(Mastered)的流程跑通。
2.  ✅ 手动标记/取消 Need Review 功能可用。
3.  ✅ 每个 Collection 显示 Need Review 数量并提供快捷入口。
4.  ✅ 数据统计准确（Attempts/Success Rate）。
