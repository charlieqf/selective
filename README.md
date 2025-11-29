# NSW Selective School Exam 学习平台

一个专门用于NSW精英中学入学考试准备的Web学习管理平台，帮助学生高效管理学习过程中遇到的难题和易错题。

## 📚 项目概述

NSW精英中学入学考试涵盖四个核心科目：Reading（阅读）、Writing（写作）、Maths（数学）、Thinking Skills（思维技能）。本平台提供便捷的题目管理、智能复习推荐和多用户协作功能。

### 核心特性

- **📱 快捷上传**：手机拍照即可上传题目
- **🎯 智能推荐**：自动追踪难题、易错题，优先推荐复习
- **👥 多角色协作**：支持学生、家长、导师三种角色
- **📊 数据可视化**：学习进度和统计分析
- **🤖 AI就绪**：为未来的AI辅助解题预留接口

## 🚀 快速开始

**👉 如果您是第一次启动项目，请先阅读 [快速开始指南](docs/00-quick-start.md)**

## 🗂️ 项目文档

所有详细文档位于 `docs/` 目录：

1. **[快速开始指南](docs/00-quick-start.md)** - 环境搭建和项目初始化
2. **[项目概述](docs/01-project-overview.md)** - 项目背景、目标和核心功能
3. **[功能需求规格](docs/02-functional-requirements.md)** - 详细的功能列表和用户故事
4. **[系统架构设计](docs/03-system-architecture.md)** - 技术栈、架构图和模块设计
5. **[数据模型设计](docs/04-data-model.md)** - 数据库Schema和关系设计
6. **[开发计划](docs/05-development-plan.md)** - 开发阶段和里程碑
7. **[UI/UX设计指南](docs/06-ui-ux-guidelines.md)** - 色彩系统、组件规范和页面设计

## 🏗️ 技术栈

### 后端
- **Framework**: Python Flask 3.0
- **ORM**: SQLAlchemy + Flask-SQLAlchemy
- **Database**: MySQL 8.0 (TiDB Cloud Serverless)
- **Authentication**: Flask-JWT-Extended
- **File Storage**: Cloudinary Python SDK

### 前端
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **UI Library**: Naive UI
- **State Manager**: Pinia
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS

### 部署
- **Frontend**: Vercel (免费)
- **Backend**: Railway (免费$5/月)
- **Database**: TiDB Cloud (免费Serverless)
- **Total Cost**: $0/月 (免费额度内)

## 📋 开发阶段

### Phase 1: MVP（6-7周）✅ 当前阶段
- [x] 项目规划文档完成
- [x] 技术栈确认（Flask + Vue + MySQL）
- [ ] Week 1: Flask后端基础 + 用户认证
- [ ] Week 2: 题目管理API + 图片上传
- [ ] Week 3: Vue前端初始化 + 登录注册
- [ ] Week 4: 题目列表和上传页面
- [ ] Week 5: 答题和推荐系统
- [ ] Week 6: Dashboard和数据可视化
- [ ] Week 7: UI优化和部署

### Phase 2: 功能增强（3-4周）
- [ ] 评论与笔记系统
- [ ] 题目分享功能
- [ ] 搜索与高级筛选
- [ ] 通知系统
- [ ] 多角色协作功能

### Phase 3: AI集成（4-6周 - 未来）
- [ ] OCR题目识别
- [ ] AI自动解答
- [ ] 智能推荐算法升级

## 🎯 下一步行动

### 本周（Week 1）
1. [ ] 注册必要服务
   - [ ] TiDB Cloud（MySQL数据库）
   - [ ] Cloudinary（图片存储）
2. [ ] 创建Flask后端项目
3. [ ] 配置数据库连接
4. [ ] 实现用户认证API
5. [ ] 测试注册登录功能

详见：[开发计划 Week 1](docs/05-development-plan.md#week-1-环境搭建与flask后端基础)

## 📖 使用场景

学生在日常学习中（纸质书、课堂）遇到难题或易错题时：
1. 📸 使用手机拍照上传题目
2. 💾 系统自动分类和存储
3. 📝 学生添加笔记、标记难度
4. 👨‍🏫 导师添加讲解和提示
5. 👨‍👩‍👦 家长查看学习进度
6. 🔄 系统智能推荐需要复习的题目

## 👥 用户角色

- **Student（学生）**：主要使用者，练习题目和复习
- **Parent（家长）**：监督和支持学生学习进度
- **Tutor（导师）**：提供专业指导和题目讲解

## 📊 项目结构

```
selective-exam-platform/
├── backend/                   # Flask后端
│   ├── app/
│   │   ├── models/           # SQLAlchemy模型
│   │   ├── routes/           # API路由(蓝图)
│   │   ├── services/         # 业务逻辑层
│   │   ├── schemas/          # Marshmallow序列化
│   │   └── utils/            # 工具函数
│   ├── migrations/           # 数据库迁移
│   ├── tests/                # 测试
│   ├── requirements.txt      # Python依赖
│   └── run.py                # 应用入口
│
├── frontend/                  # Vue前端
│   ├── src/
│   │   ├── api/              # API调用
│   │   ├── components/       # Vue组件
│   │   ├── views/            # 页面组件
│   │   ├── stores/           # Pinia状态管理
│   │   ├── router/           # Vue Router
│   │   └── utils/            # 工具函数
│   ├── package.json          # Node依赖
│   └── vite.config.js        # Vite配置
│
└── docs/                      # 项目文档
```

## 🛠️ 开发命令

### 后端（Flask）
```bash
# 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 运行开发服务器
flask run

# 数据库迁移
f lask db migrate -m "description"
flask db upgrade
```

### 前端（Vue）
```bash
# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 📄 License

本项目为私人项目，用于教育目的。

---

**开始日期**: 2025-11-23  
**当前状态**: 📝 规划完成，准备开发  
**技术栈**: Flask + Vue + MySQL  
**预计MVP完成**: 6-7周后
