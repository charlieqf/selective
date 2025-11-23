# 开发计划与实施路线图 - Flask + Vue版本

## 1. 项目阶段划分

### Phase 1: MVP（最小可行产品）- 6-7周
**目标**：实现核心功能，验证产品价值

### Phase 2: 功能增强 - 3-4周
**目标**：完善用户体验，增加协作功能

### Phase 3: AI功能集成 - 4-6周（未来规划）
**目标**：接入AI服务，提升智能化水平

---

## 2. Phase 1 详细计划（MVP）- 6-7周

### Week 1: 环境搭建与Flask后端基础

**目标**：完成Flask项目初始化和用户认证

#### 任务清单

**Day 1-2: 项目初始化**
- [x] 技术栈确认
- [ ] 注册必要服务
  - [ ] PlanetScale（MySQL数据库）
  - [ ] Cloudinary（图片存储）
  - [ ] Vercel（前端部署）
  - [ ] Railway（后端部署）
- [ ] 创建Flask项目结构
  ```bash
  mkdir backend
  cd backend
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  ```
- [ ] 安装依赖
  ```bash
  pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-JWT-Extended Flask-CORS Flask-Marshmallow PyMySQL python-dotenv bcrypt cloudinary
  ```
- [ ] 创建requirements.txt
  ```bash
  pip freeze > requirements.txt
  ```

**Day 3-4: 数据库设置**
- [ ] 配置PlanetScale数据库
- [ ] 创建SQLAlchemy模型（User, Profile, StudyStats）
- [ ] 初始化Flask-Migrate
  ```bash
  flask db init
  flask db migrate -m "Initial schema"
  flask db upgrade
  ```
- [ ] 测试数据库连接

**Day 5-7: 用户认证**
- [ ] 实现User模型和密码加密
- [ ] 创建认证API
  - [ ] POST /api/auth/register（注册）
  - [ ] POST /api/auth/login（登录）
  - [ ] GET /api/auth/me（获取当前用户）
- [ ] Flask-JWT-Extended配置
- [ ] 编写认证装饰器
- [ ] 测试认证API（Postman/Thunder Client）

**交付物**：
- ✅ Flask项目可运行
- ✅ 数据库连接成功
- ✅ 用户可以注册和登录
- ✅ JWT Token认证工作

---

### Week 2: Flask题目管理API

**目标**：完成题目CRUD和图片上传

#### 任务清单

**Day 1-2: 题目模型和基础API**
- [ ] 创建Question, Answer模型
- [ ] 数据库迁移
  ```bash
  flask db migrate -m "Add Question and Answer models"
  flask db upgrade
  ```
- [ ] 实现QuestionService业务逻辑
- [ ] 创建题目CRUD API
  - [ ] GET /api/questions（列表，支持筛选）
  - [ ] POST /api/questions（创建）
  - [ ] GET /api/questions/<id>（详情）
  - [ ] PATCH /api/questions/<id>（更新）
  - [ ] DELETE /api/questions/<id>（删除）

**Day 3-4: 图片上传**
- [ ] 配置Cloudinary Python SDK
- [ ] 创建UploadService
  - [ ] 图片上传到Cloudinary
  - [ ] 生成缩略图
  - [ ] 返回URLs
- [ ] 创建上传API
  - [ ] POST /api/upload（单张图片）
  - [ ] POST /api/upload/multiple（多张图片）
- [ ] 测试图片上传

**Day 5-7: 题目筛选和分页**
- [ ] 实现筛选逻辑
  - [ ] 按科目筛选
  - [ ] 按难度筛选
  - [ ] 按状态筛选
  - [ ] 按难题/易错题筛选
- [ ] 实现排序
  - [ ] 最新上传
  - [ ] 难度排序
  - [ ] 创建时间排序
- [ ] 实现分页
- [ ] 优化查询性能
- [ ] 测试各种筛选组合

**交付物**：
- ✅ 题目可以创建、查询、更新、删除
- ✅ 图片可以上传到Cloudinary
- ✅ 筛选和分页工作正常

---

### Week 3: Vue前端项目初始化

**目标**：搭建Vue项目，实现登录注册

#### 学习资源（如需要）
- [Vue 3官方教程](https://cn.vuejs.org/guide/quick-start.html) - 1-2天
- [Pinia状态管理](https://pinia.vuejs.org/zh/) - 半天
- [Vue Router](https://router.vuejs.org/zh/) - 半天

#### 任务清单

**Day 1-2: 项目初始化**
- [ ] 创建Vue项目
  ```bash
  npm create vite@latest frontend -- --template vue
  cd frontend
  npm install
  ```
- [ ] 安装依赖
  ```bash
  npm install vue-router pinia axios
  npm install naive-ui
  npm install -D tailwindcss postcss autoprefixer
  npx tailwindcss init -p
  ```
- [ ] 配置Tailwind CSS
- [ ] 配置Vue Router
- [ ] 配置Pinia
- [ ] 项目结构搭建

**Day 3-4: API客户端和认证Store**
- [ ] 创建Axios客户端（src/api/client.js）
- [ ] 配置请求/响应拦截器
- [ ] 创建authStore（Pinia）
  - [ ] login action
  - [ ] register action
  - [ ] logout action
  - [ ] token管理
- [ ] 创建认证API调用（src/api/auth.js）

**Day 5-7: 登录注册页面**
- [ ] 创建AuthLayout布局
- [ ] 创建登录页面
  - [ ] 表单设计
  - [ ] 表单验证
  - [ ] 提交登录
  - [ ] 错误处理
- [ ] 创建注册页面
  - [ ] 表单设计
  - [ ] 角色选择
  - [ ] 提交注册
- [ ] 路由守卫（未登录重定向）
- [ ] 测试登录注册流程

**交付物**：
- ✅ Vue项目可运行
- ✅ 可以通过前端登录/注册
- ✅ Token自动添加到请求头
- ✅ 登录后跳转到Dashboard

---

### Week 4: Vue题目管理页面

**目标**：实现题目列表、上传、详情页面

#### 任务清单

**Day 1-2: 题目列表页面**
- [ ] 创建questionStore（Pinia）
- [ ] 创建题目API调用（src/api/questions.js）
- [ ] 创建QuestionCard组件
- [ ] 创建QuestionList页面
  - [ ] 题目网格布局
  - [ ] 加载状态
  - [ ] 空状态
- [ ] 测试列表展示

**Day 3-4: 筛选和排序**
- [ ] 创建QuestionFilters组件
  - [ ] 科目筛选器
  - [ ] 难度筛选器
  - [ ] 状态筛选器
  - [ ] 排序选择器
- [ ] 集成到QuestionList
- [ ] 测试筛选功能

**Day 5-7: 题目上传**
- [ ] 创建QuestionUpload页面
- [ ] 文件上传组件
  - [ ] 图片预览
  - [ ] 裁剪功能（可选）
  - [ ] 多图上传
- [ ] 题目信息表单
  - [ ] 科目选择
  - [ ] 标签输入
  - [ ] 难度评分
- [ ] 上传流程
  1. 上传图片到API
  2. 获取URLs
  3. 提交题目信息
- [ ] 测试上传流程

**交付物**：
- ✅ 可以查看题目列表
- ✅ 可以筛选和排序
- ✅ 可以上传新题目
- ✅ 移动端上传体验良好

---

### Week 5: 答题和推荐系统

**目标**：实现答题功能和推荐算法

#### 任务清单

**Day 1-2: 答题API（Flask）**
- [ ] 创建Answer模型（如Week 2未完成）
- [ ] 实现AnswerService
- [ ] 创建答案API
  - [ ] POST /api/answers（提交答案）
  - [ ] GET /api/questions/<id>/answers（获取答题历史）
- [ ] 更新题目统计
  - [ ] answer_count
  - [ ] correct_count
  - [ ] 自动标记is_frequent_error

**Day 3-4: 推荐算法（Flask）**
- [ ] 创建RecommendationService
- [ ] 实现优先级计算
  ```python
  priority = error_rate * 0.4 + difficulty * 0.3 + time_decay * 0.2 + (1 - mastery) * 0.1
  ```
- [ ] 创建推荐API
  - [ ] GET /api/recommendations（获取推荐列表）
  - [ ] GET /api/recommendations/subject/<subject>（按科目推荐）
- [ ] 测试推荐逻辑

**Day 5-7: 答题页面（Vue）**
- [ ] 创建QuestionDetail页面
  - [ ] 题目图片展示（可缩放）
  - [ ] 题目信息展示
  - [ ] 答题区域
  - [ ] 提交按钮
- [ ] 答题表单
  - [ ] 答案输入
  - [ ] 正确/错误标记
  - [ ] 掌握程度评分
- [ ] 答题历史展示
- [ ] 测试答题流程

**交付物**：
- ✅ 可以在线答题
- ✅ 答题记录保存
- ✅ 推荐算法返回合理结果
- ✅ 题目统计自动更新

---

### Week 6: Dashboard和数据可视化

**目标**：实现Dashboard和统计图表

#### 任务清单

**Day 1-2: 统计API（Flask）**
- [ ] 创建AnalyticsService
- [ ] 实现统计计算
- [ ] 创建统计API
  - [ ] GET /api/analytics/stats（总体统计）
  - [ ] GET /api/analytics/subject-stats（各科统计）
  - [ ] GET /api/analytics/trend（趋势数据）
  - [ ] GET /api/analytics/weak-points（薄弱点）

**Day 3-5: Dashboard页面（Vue）**
- [ ] 创建StatsCard组件（统计卡片）
- [ ] 创建RecommendationList组件
- [ ] 创建ProgressChart组件（使用Vue-ECharts）
- [ ] 创建Dashboard页面
  - [ ] 欢迎信息
  - [ ] 快速统计（4个卡片）
  - [ ] 今日推荐（横向滚动）
  - [ ] 学习趋势图表
  - [ ] 各科目进度
- [ ] 响应式布局

**Day 6-7: 科目板块页面**
- [ ] 创建ReadingView
- [ ] 创建WritingView
- [ ] 创建MathsView
- [ ] 创建ThinkingView
- [ ] 每个页面包含：
  - [ ] 科目统计概览
  - [ ] 筛选后的题目列表
  - [ ] 推荐复习题目

**交付物**：
- ✅ Dashboard展示完整数据
- ✅ 图表可视化清晰
- ✅ 4个科目板块完成
- ✅ 响应式设计良好

---

### Week 7: UI优化和部署

**目标**：优化界面，部署上线

#### 任务清单

**Day 1-2: UI/UX优化**
- [ ] 移动端适配检查
- [ ] 加载状态优化
- [ ] 错误提示优化
- [ ] 动画效果添加
- [ ] 空状态设计
- [ ] 404页面

**Day 3-4: 性能优化**
- [ ] 前端代码分割
- [ ] 图片懒加载
- [ ] API响应缓存
- [ ] 减少不必要的请求
- [ ] Lighthouse性能测试

**Day 5-6: 部署**
- [ ] **前端部署（Vercel）**
  1. 连接GitHub仓库
  2. 配置环境变量
     ```
     VITE_API_URL=https://api.yourapp.com
     ```
  3. 自动部署
  
- [ ] **后端部署（Railway）**
  1. 连接GitHub仓库
  2. 配置环境变量
     ```
     DATABASE_URL=mysql://...
     JWT_SECRET_KEY=...
     CLOUDINARY_*=...
     CORS_ORIGINS=https://yourapp.com
     ```
  3. 配置启动命令
     ```
     gunicorn -w 4 -b 0.0.0.0:$PORT run:app
     ```
  4. 部署

- [ ] **数据库（PlanetScale）**
  - 已在开发中使用，无需额外配置

**Day 7: 测试**
- [ ] 端到端功能测试
- [ ] 不同设备测试（手机、平板、桌面）
- [ ] 真机测试（iOS、Android）
- [ ] 性能测试
- [ ] 修复发现的问题

**交付物**：
- ✅ MVP完整功能上线
- ✅ 移动端体验良好
- ✅ 性能达标
- ✅ 部署稳定

---

## 3. Phase 2 详细计划（功能增强）- 3-4周

### Week 8-9: 协作功能

**Flask后端**:
- [ ] Comment, Note模型
- [ ] 评论CRUD API
- [ ] 笔记CRUD API
- [ ] 题目分享API

**Vue前端**:
- [ ] 评论组件（支持嵌套回复）
- [ ] 笔记编辑器（富文本）
- [ ] 分享对话框
- [ ] 通知提示

### Week 10: 搜索和高级功能

**Flask后端**:
- [ ] 搜索API（LIKE查询或全文索引）
- [ ] 家长-学生关联API
- [ ] 导师-学生关联API

**Vue前端**:
- [ ] 搜索组件
- [ ] 用户管理页面
- [ ] 角色专属功能

### Week 11: 通知和设置

**Flask后端**:
- [ ] Notification模型
- [ ] 通知API
- [ ] 用户设置API

**Vue前端**:
- [ ] 通知中心
- [ ] 用户设置页面
- [ ] 头像上传
- [ ] 偏好设置

---

## 4. Phase 3 计划（AI集成）- 未来

### Week 12-13: OCR功能
- [ ] 集成OCR API（Google Cloud Vision / Azure）
- [ ] 题目文字识别
- [ ] 自动分类

### Week 14-16: AI解答
- [ ] 集成AI API（OpenAI / Google Gemini）
- [ ] AI题目讲解
- [ ] 智能推荐优化

---

## 5. 技术里程碑

### Milestone 1: MVP上线（Week 7）
- ✅ 用户注册登录
- ✅ 题目上传（手机拍照）
- ✅ 题目浏览和筛选
- ✅ 在线答题
- ✅ 智能推荐
- ✅ Dashboard统计
- ✅ 四个科目板块

**验收标准**：
- 学生可以完整使用：注册→上传→答题→查看推荐→复习
- 移动端拍照上传流畅
- 推荐算法合理

### Milestone 2: 功能完善（Week 11）
- ✅ 评论和笔记
- ✅ 题目分享
- ✅ 搜索功能
- ✅ 多角色功能

### Milestone 3: AI增强（Week 16）
- ✅ OCR识别
- ✅ AI解答

---

## 6. 每日开发建议

### 开发节奏
- **上午**（3-4小时）：核心功能开发
- **下午**（2-3小时）：测试和调试
- **晚上**（1小时）：学习新知识（如果需要）

### 开发顺序建议
1. **先后端后前端** - 确保API可用再开发UI
2. **先核心后优化** - 功能优先，性能和美化其次
3. **小步迭代** - 每完成一个小功能就测试
4. **频繁提交** - 每天至少1次Git commit

### 遇到问题时
1. 查官方文档
2. 搜索Stack Overflow
3. 使用AI助手（Claude、ChatGPT）
4. 简化问题，逐步调试

---

## 7. 学习时间预算

### Flask（您已熟悉）
- ✅ 0天 - 直接开发

### Vue 3学习（如需要）
- Day 1-2: Vue基础（组件、响应式、指令）
- Day 3: Composition API
- Day 4: Vue Router + Pinia
- Day 5: 练习项目

**总计**：5天可以掌握足够开发的知识

### 建议
- 边学边做，不要等完全学会再开始
- 遇到问题现学现查
- Week 3专注于学习Vue，Week 4开始开发

---

## 8. 成本估算

### 开发阶段（Week 1-7）
- PlanetScale: $0（免费5GB）
- Cloudinary: $0（免费25GB）
- Vercel: $0（免费）
- Railway: $0（免费$5/月额度）
- **总计**: $0/月

### 小规模生产（<1000用户）
- PlanetScale: $0-29/月
- Cloudinary: $0
- Vercel: $0
- Railway: $5-10/月
- **总计**: $5-39/月

---

## 9. 风险与应对

### 技术风险

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| Vue学习曲线 | 中 | 中 | 预留5天学习时间 |
| API集成问题 | 低 | 中 | 充分测试，提前准备 |
| 部署问题 | 中 | 高 | 提前熟悉部署流程 |
| 性能问题 | 低 | 中 | 数据库索引，代码优化 |

### 时间风险

| 风险 | 应对 |
|------|------|
| 某个功能比预期复杂 | MVP阶段简化实现 |
| 学习时间超出预期 | 减少非核心功能 |
| 意外Bug | 每天预留1小时调试时间 |

---

## 10. 下一步行动

### 本周（Week 1）
1. [ ] 注册所有必要服务
2. [ ] 创建Flask项目
3. [ ] 配置数据库
4. [ ] 实现用户认证
5. [ ] 测试注册登录

### 第一个里程碑（Week 7后）
- ✅ MVP部署上线
- ✅ 您儿子可以开始使用
- ✅ 收集真实使用反馈

### 成功标准
- 学生每周至少使用3次
- 上传题目>50道
- 推荐题目被复习率>60%

---

## 11. 开发环境配置清单

### 必需软件
- [x] Python 3.9+
- [x] Node.js 18+
- [x] Git
- [ ] VS Code + 推荐扩展
  - Python
  - Volar (Vue)
  - Tailwind CSS IntelliSense
  - SQLTools

### 账号注册
- [ ] PlanetScale
- [ ] Cloudinary
- [ ] Vercel
- [ ] Railway
- [ ] GitHub（代码托管）

### 环境变量模板

**后端 (.env)**:
```bash
DATABASE_URL=mysql+pymysql://...
JWT_SECRET_KEY=your-secret-key
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
CORS_ORIGINS=http://localhost:5173,https://yourapp.com
```

**前端 (.env)**:
```bash
VITE_API_URL=http://localhost:5000
```

---

**准备好开始了吗？** 🚀

从Week 1 Day 1开始，我会一步步陪您完成整个开发！
