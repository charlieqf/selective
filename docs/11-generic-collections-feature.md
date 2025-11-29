# Generic Collections Feature Design

## 1. 核心概念变更

**目标**：将 "Subject" (科目) 泛化，使其适用于多种场景（学习、练琴、工作记录等）。

**建议命名**：
*   **Option A: "Topic" (主题)** - 强调内容的主题性。适合：学习、讨论、分类。
*   **Option B: "Collection" (合集)** - 强调内容的集合。适合：相册、项目资料、作品集。
        *   数据库中不设置 `name` 的唯一索引。
        *   允许存在多条同名记录（例如多条 "Maths"），它们通过唯一的 `id` 主键区分。
        *   **应用层逻辑**：在创建或重命名时，检查当前用户下是否存在 **is_deleted=False** 且同名的记录。如果存在则报错。
        *   这样，回收站里可以有多个 "Maths" (ID=1, ID=2...)，但活跃列表里只能有一个。
    *   **恢复时检查**：如果尝试从回收站恢复 "Maths"，但当前已经存在一个活跃的 "Maths"，系统提示用户重命名或先处理活跃的那个。

### 2.2 软删除 (Soft Delete)与恢复
*   **删除动作**：用户点击删除 -> Topic 进入 "Trash" (回收站) 状态。
*   **表现**：
    *   该 Topic 不再出现在正常列表中。
    *   该 Topic 下的题目/内容暂时隐藏（或在"回收站"中可见）。
*   **恢复**：用户可以在"回收站"中恢复该 Topic。
*   **彻底删除**：
    *   用户在"回收站"中选择"彻底删除"。
    *   **Cascade Delete**：彻底删除 Collection 时，**物理删除**该 Collection 下的所有 Question/Content 的数据库记录。
    *   **Performance Optimization**: 为了避免请求超时，**不会**同步删除 Cloudinary 上的图片/文件。
    *   **Cleanup Strategy**: Cloudinary 上的孤儿文件（Orphaned Files）将通过定期的后台任务（Cron Job）进行清理（对比数据库中的 active/deleted items 与 Cloudinary 资源列表）。

### 2.3 为什么需要独立的 `collections` 表？ (Rationale)

你可能会问，为什么不直接在 `Question` 表里保留 `subject` 字符串字段？

1.  **重命名的一致性 (Renaming Consistency)**:
    *   如果使用字符串字段，将 "Maths" 重命名为 "Mathematics" 需要更新成千上万条 `Question` 记录。
    *   使用独立的表，只需更新 `collections` 表中的一行记录，所有关联的题目会自动指向新的名称。

2.  **元数据存储 (Metadata Storage)**:
    *   我们需要为每个合集存储额外的属性，如**图标 (icon)**、**颜色 (color)**、**描述**等。
    *   如果没有独立的表，这些数据将无处安放，或者需要在每一条题目中重复存储（冗余）。

3.  **数据完整性 (Data Integrity)**:
    *   防止拼写错误（例如 "Maths" 和 "Math" 被视为两个不同的科目）。
    *   通过外键约束（Foreign Key），确保题目总是属于一个有效的合集。

4.  **性能 (Performance)**:
    *   获取用户的所有合集列表时，查询一个小型的 `collections` 表比扫描巨大的 `questions` 表并进行 `DISTINCT` 操作要快得多。

---

## 3. 数据模型设计

### 3.1 New Model: `Collection`

```python
class Collection(db.Model):
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50))  # 可选图标
    color = db.Column(db.String(20)) # 可选颜色
    
    # Soft Delete
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    # 关键：使用 deleted_at 区分不同的删除版本
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Uniqueness Constraint
    # MySQL/TiDB treats NULLs as distinct for UNIQUE constraints.
    # So (user_id, name, deleted_at) allows multiple (1, 'Maths', NULL) -> NO, we want only ONE NULL.
    # Wait, MySQL allows multiple NULLs in unique index. So (1, 'Maths', NULL) and (1, 'Maths', NULL) are allowed.
    # This is NOT what we want for Active items.
    
    # Correct Strategy for MySQL/TiDB (Database Constraint):
    # We want uniqueness on (user_id, name) ONLY when is_deleted is False.
    # MySQL does not support "Partial Indexes" (WHERE clause).
    # Solution: Use a **Generated Column** (Virtual Column).
    # 
    # 1. Add column `active_name` defined as:
    #    `CASE WHEN is_deleted = 0 THEN name ELSE NULL END`
    # 2. Add UNIQUE INDEX on `(user_id, active_name)`.
    # 
    # Behavior:
    # - Active "Maths": active_name="Maths". Conflict if another "Maths" exists.
    # - Deleted "Maths": active_name=NULL. Multiple NULLs allowed in MySQL unique index.
    # 
    # This enforces the invariant at the database level, preventing race conditions without explicit locking.
```

### 3.2 Rename Model: `Question` -> `Item`

为了支持未来的扩展性（不仅仅是题目），我们将 `Question` 模型重命名为 `Item`。

**关键策略：后端重构，前端兼容 (Backend Refactor, Frontend Compatibility)**

*   **Database**: 表名从 `questions` 变为 `items`。
*   **Model**: Python 类名从 `Question` 变为 `Item`。
*   **API Surface**: 
    *   保持 `/api/questions` 路由（或作为 `/api/items` 的别名）。
    *   API 响应字段保持不变（例如前端期望 `subject`，后端 `Item` 可能存储为 `collection_id`，但在序列化时动态查找并返回 `subject` 名称，或者前端适配）。
    *   **目标**：确保现有的前端代码和 UI 测试（Playwright）**不需要修改**（或只需极小修改）即可通过。
*   **Terminology**: 
    *   用户界面仍然显示 "Question", "Subject"。
    *   代码内部（后端）使用 "Item", "Collection"。

```python
class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    # ... existing fields (title, content_text, difficulty, etc.) ...
    
    # Foreign Key to Collection
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=True) 
    
    # Polymorphic type (Optional for future, e.g., 'question', 'post', 'image')
    # type = db.Column(db.String(20), default='question') 
```

---

## 4. 迁移策略 (Migration Strategy)

1.  **Create Table**: 创建 `collections` 表。
2.  **Data Migration**: 
    *   遍历所有现有的 `Question`。
    *   读取 `subject` 字段 (e.g., "MATHS")。
    *   在 `collections` 表中查找或创建对应的 Collection (name="Maths")。
    *   更新 `Question.collection_id`。
3.  **Cleanup**: 删除 `Question.subject` 字段（或保留作为备份）。

---

## 5. API 变更

*   `GET /api/collections`: 获取所有活跃 Collection。
*   `POST /api/collections`: 创建 Collection (Check unique active).
*   `PATCH /api/collections/<id>`: 重命名/软删除。
*   `DELETE /api/collections/<id>`: 彻底删除 (Cascade)。
*   `GET /api/collections/trash`: 获取回收站内容。
*   `POST /api/collections/<id>/restore`: 恢复 (Check unique active).

### 5.2 Item API (Renamed from Question)

*   **Endpoint**: `/api/items` (Replaces `/api/questions`).
*   **Strategy**: Full Replacement (Clean Break).
    *   We will **remove** `/api/questions` entirely.
    *   Frontend code will be updated to call `/api/items`.
    *   Frontend UI terminology can remain "Question" for now, but the data fetching layer will use "Item".

*   `GET /api/items`: List items.
*   `POST /api/items`: Create item.
*   `GET /api/items/<id>`: Get item detail.
*   `PATCH /api/items/<id>`: Update item.
*   `DELETE /api/items/<id>`: Delete item.

---

### 6.1 默认合集 (Default Collections)

为了保持 "Selective School Exam Prep" 的核心定位，我们将为每个新用户默认创建以下 4 个合集：

1.  **Reading**
2.  **Writing**
3.  **Maths**
4.  **Thinking Skills**

*   **注册时机**: 用户注册成功后，系统自动创建这 4 个 Collection 记录。
*   **迁移逻辑**: 现有的 `Question` 数据将根据其 `subject` 字段自动映射到上述对应的 Collection 中（即设置 `item.collection_id`）。
*   **未来扩展**: 暂时不开放用户自定义创建/删除 Collection 的功能（UI 上隐藏），未来版本再开放。

### 6.2 讨论点
1.  **命名**: 已确认为 **Collection**。
2.  **默认Collection**: 确认实施上述 4 个默认科目。
