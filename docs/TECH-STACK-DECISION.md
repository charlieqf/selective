# 技术栈最终决策

> **状态**: ✅ 已确认并锁定  
> **决策日期**: 2025-11-23  
> **生效范围**: 整个项目

---

## 📋 最终技术栈

### 后端
- **框架**: Python Flask 3.0 ✅ 已锁定
- **ORM**: SQLAlchemy 2.0
- **数据库**: MySQL 8.0 (TiDB Cloud Serverless)
- **认证**: Flask-JWT-Extended

### 前端
- **框架**: Vue 3 (Composition API) ✅ 已锁定
- **构建工具**: Vite
- **UI库**: Naive UI
- **状态管理**: Pinia

### 部署
- **前端**: Vercel
- **后端**: Railway
- **数据库**: TiDB Cloud

---

## 🔒 决策原因

### 为什么选择 Flask + Vue 而非 Next.js？

1. **用户熟悉度**: 您熟悉Python Flask和MySQL
2. **学习曲线**: Vue比React略简单
3. **独立开发**: 前后端分离，职责清晰
4. **成本**: 全部免费额度可用

### 为什么选择 MySQL 而非 PostgreSQL？

1. **熟悉度**: 您更熟悉MySQL
2. **TiDB Cloud**: 提供优秀的MySQL Serverless托管服务（永久免费）
3. **性能**: MySQL 8.0对JSON支持已足够

---

## ⛔ 不再考虑的选项

以下技术栈已被**正式排除**，不再作为备选方案：

### ❌ Next.js 全栈方案
- 理由: 用户不熟悉TypeScript和React
- 文档: 已清理所有Next.js相关描述

### ✅ 使用 String 而非 Enum

**位置**: Question.subject, Question.status

**原因**:
1. 支持未来自定义科目扩展
2. 避免数据库迁移复杂性
3. 提供更大灵活性

**实现**:
```python
# ✅ 正确做法
subject = db.Column(db.String(50), nullable=False)

# ❌ 已废弃
subject = db.Column(db.Enum('READING', 'WRITING', ...))
```

### ✅ MVP简化内容模型

**位置**: Question内容存储

**MVP阶段**:
```python
image_urls = db.Column(db.JSON)  # ["url1.jpg", "url2.jpg"]
description = db.Column(db.Text)  # 可选说明文字
```

**Phase 2扩展**:
```python
content = db.Column(db.JSON)  # 完整的content JSON结构
# 见 docs/11-flexible-content-design.md
```

---

## ✅ UI框架决策

### Naive UI (不是 shadcn/ui)

**原因**:
- Naive UI 是 Vue 3 专用
- shadcn/ui 是 React 专用
- Naive UI 提供完整组件库

**已清理**:
- ❌ 删除所有 shadcn/ui 引用
- ❌ 删除所有 React/TSX 代码示例
- ✅ 更新为 Vue/Naive UI 示例

---

## 📚 文档更新记录

### 已修复的文档

1. ✅ `docs/README.md` (51-72行)
   - Next.js → Flask + Vue

2. ✅ `docs/03-system-architecture.md` (348,356行)
   - Enum → String

3. ✅ `docs/06-ui-ux-guidelines.md` (603-658行)
   - React → Vue代码示例
   - shadcn/ui → Naive UI

4. ✅ `docs/04-data-model.md`
   - 已使用String定义

5. ✅ `backend/`实际代码
   - config.py 使用 SUBJECTS 配置
   - 无Enum定义

### 历史文档（仅供参考）

- `docs/08-tech-stack-flask.md` - 决策过程记录
- `docs/09-decision-guide.md` - 决策指南
- `docs/10-custom-subjects-feature.md` - 未来扩展设计

---

## 🎯 开发指导原则

### 从现在开始

1. **所有新代码**: 使用Flask + Vue + MySQL
2. **数据类型**: 使用String，不用Enum
3. **UI组件**: 使用Naive UI，不用shadcn/ui
4. **代码示例**: 使用Vue，不用React
5. **API**: RESTful，不用GraphQL

### 如有疑问

1. 查看 `QUICKSTART.md` - 立即开始
2. 查看 `docs/04-data-model.md` - 数据模型
3. 查看 `docs/03-system-architecture.md` - 架构设计
4. **不要**参考任何Next.js / React相关内容

---

## 📅 时间线

- 2025-11-23: 技术栈确认
- 2025-11-23: 文档全面更新
- **从现在起**: 严格遵守此技术栈

---

**此决策为最终决策，不再变更。**
