# 快速开始指南 - Flask + Vue + MySQL

本指南帮助您快速启动NSW Selective School Exam学习平台项目。

## 📋 准备工作

### 1. 系统要求

- **Python**: 3.9 或更高版本
- **Node.js**: 18.0 或更高版本
- **npm/yarn**: 最新版本
- **Git**: 用于版本控制
- **代码编辑器**: VS Code（推荐）

### 2. 注册必需的服务账号

#### 2.1 PlanetScale（MySQL数据库）⭐推荐

1. 访问 https://planetscale.com
2. 使用GitHub账号注册
3. 创建新数据库：
   - Database name: `selective-exam-platform`
   - Region: `AWS ap-southeast-2` (Sydney - 离澳洲最近)
4. 创建密码（Create password）
   - Name: `development`
   - 复制连接字符串
5. **重要**: 保存连接字符串，格式如下：
   ```
   mysql://username:password@aws.connect.psdb.cloud/selective-exam-platform?ssl={"rejectUnauthorized":true}
   ```

#### 2.2 Cloudinary（图片存储）

1. 访问 https://cloudinary.com
2. 注册免费账号
3. 登录后，进入Dashboard
4. 记录以下信息：
   - **Cloud Name**: 页面顶部显示
   - **API Key**: Account Details中
   - **API Secret**: 点击眼睛图标查看
5. 创建Upload Preset:
   - Settings → Upload → Add upload preset
   - Preset name: `selective-questions`
   - Signing Mode: `Unsigned`
   - Save

#### 2.3 Vercel（前端部署 - 可选，开发阶段不需要）

1. 访问 https://vercel.com
2. 使用GitHub账号注册
3. 稍后部署时再配置

#### 2.4 Railway（后端部署 - 可选，开发阶段不需要）

1. 访问 https://railway.app
2. 使用GitHub账号注册
3. 稍后部署时再配置

---

## 🚀 项目初始化

### Part A: Flask后端设置

#### Step 1: 创建项目目录

```bash
mkdir selective-exam-platform
cd selective-exam-platform

# 创建后端目录
mkdir backend
cd backend
```

#### Step 2: 创建Python虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

成功激活后，命令行前面会显示 `(venv)`

#### Step 3: 安装Python依赖

```bash
# 创建requirements.txt
cat > requirements.txt << EOF
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.5
Flask-JWT-Extended==4.6.0
Flask-CORS==4.0.0
Flask-Marshmallow==0.15.0
marshmallow-sqlalchemy==0.29.0
PyMySQL==1.1.1
python-dotenv==1.0.0
bcrypt==4.1.2
cloudinary==1.40.0
gunicorn==21.2.0
EOF

# 安装依赖
pip install -r requirements.txt
```

#### Step 4: 创建Flask项目结构

```bash
# 创建目录结构
mkdir -p app/models app/routes app/services app/schemas app/utils
mkdir migrations tests

# 创建__init__.py文件
touch app/__init__.py
touch app/models/__init__.py
touch app/routes/__init__.py
touch app/services/__init__.py
touch app/schemas/__init__.py
touch app/utils/__init__.py
```

#### Step 5: 配置环境变量

创建 `.env` 文件：

```bash
# .env
DATABASE_URL=mysql+pymysql://[从PlanetScale复制]
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
FLASK_APP=run.py
FLASK_ENV=development
CORS_ORIGINS=http://localhost:5173
```

**生成SECRET_KEY**:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

#### Step 6: 创建Flask应用工厂

创建 `app/__init__.py`:

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)
    
    # CORS配置
    CORS(app, resources={
        r"/api/*": {
            "origins": os.environ.get('CORS_ORIGINS', '').split(','),
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册蓝图（暂时注释，后续添加）
    # from app.routes import auth, questions
    # app.register_blueprint(auth.bp)
    # app.register_blueprint(questions.bp)
    
    return app
```

创建 `run.py`:

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

#### Step 7: 测试Flask应用

```bash
flask run
```

访问 http://localhost:5000，应该看到"404 Not Found"（正常，因为还没有路由）

#### Step 8: 初始化数据库迁移

```bash
flask db init
```

这会创建 `migrations` 目录。

---

### Part B: Vue前端设置

#### Step 1: 创建Vue项目

回到项目根目录：

```bash
cd ..  # 回到selective-exam-platform目录

# 创建Vue项目
npm create vite@latest frontend -- --template vue
cd frontend
```

#### Step 2: 安装前端依赖

```bash
# 核心依赖
npm install

# 路由和状态管理
npm install vue-router@4 pinia

# HTTP客户端
npm install axios

# UI库（选择Naive UI）
npm install naive-ui

# 图标
npm install @vicons/ionicons5

# 表单验证
npm install vee-validate yup

# 工具库
npm install date-fns

# 图表
npm install echarts vue-echarts

# Tailwind CSS
npm install -D tailwindcss@latest postcss@latest autoprefixer@latest
npx tailwindcss init -p
```

#### Step 3: 配置Tailwind CSS

编辑 `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        reading: '#f97316',
        writing: '#a855f7',
        maths: '#10b981',
        thinking: '#6366f1',
      }
    },
  },
  plugins: [],
}
```

创建 `src/assets/main.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

在 `src/main.js` 中导入：

```javascript
import './assets/main.css'
```

#### Step 4: 配置环境变量

创建 `.env`:

```bash
VITE_API_URL=http://localhost:5000
```

#### Step 5: 创建Vue项目结构

```bash
mkdir -p src/api src/components/common src/components/questions src/components/dashboard
mkdir -p src/composables src/layouts src/router src/stores src/views src/utils
```

#### Step 6: 配置Axios客户端

创建 `src/api/client.js`:

```javascript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

#### Step 7: 配置Vue Router

创建 `src/router/index.js`:

```javascript
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/dashboard'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/auth/LoginView.vue')
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/dashboard/DashboardView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

#### Step 8: 配置Pinia

创建 `src/stores/auth.js`:

```javascript
import { defineStore } from 'pinia'
import apiClient from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.token
  },

  actions: {
    async login(email, password) {
      const response = await apiClient.post('/api/auth/login', { email, password })
      this.token = response.data.access_token
      this.user = response.data.user
      localStorage.setItem('access_token', this.token)
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('access_token')
    }
  }
})
```

#### Step 9: 更新main.js

编辑 `src/main.js`:

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import naive from 'naive-ui'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(naive)

app.mount('#app')
```

#### Step 10: 测试Vue应用

```bash
npm run dev
```

访问 http://localhost:5173，应该看到Vue默认页面。

---

## ✅ 验证安装

### 1. 测试Flask后端

在backend目录：

```bash
# 激活虚拟环境（如果未激活）
source venv/bin/activate  # Windows: venv\Scripts\activate

# 运行Flask
flask run
```

应该看到：
```
* Running on http://127.0.0.1:5000
```

### 2. 测试Vue前端

在frontend目录：

```bash
npm run dev
```

应该看到：
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### 3. 测试数据库连接

创建一个测试路由 `app/routes/test.py`:

```python
from flask import Blueprint, jsonify
from app import db

bp = Blueprint('test', __name__, url_prefix='/api/test')

@bp.route('/db', methods=['GET'])
def test_db():
    try:
        db.session.execute('SELECT 1')
        return jsonify({'status': 'ok', 'message': 'Database connected'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

在 `app/__init__.py` 中注册：

```python
from app.routes import test
app.register_blueprint(test.bp)
```

访问 http://localhost:5000/api/test/db，应该看到：
```json
{
  "status": "ok",
  "message": "Database connected"
}
```

---

## 📝 下一步

安装完成后，按照以下顺序开始开发：

### Week 1: Flask后端基础
1. **创建User模型**（参考 `docs/04-data-model.md`）
2. **实现用户认证API**
   - POST /api/auth/register
   - POST /api/auth/login
3. **测试认证功能**

### Week 2: 题目管理API
1. **创建Question模型**
2. **实现题目CRUD API**
3. **实现图片上传**

### Week 3: Vue前端开发
1. **学习Vue基础**（如需要，1-2天）
2. **创建登录注册页面**
3. **测试前后端联调**

详细计划请参考：[开发计划](05-development-plan.md)

---

## 🔧 常用命令

### Flask后端

```bash
# 激活虚拟环境
source venv/bin/activate  # Windows: venv\Scripts\activate

# 运行开发服务器
flask run

# 数据库迁移
flask db migrate -m "description"
flask db upgrade

# 查看数据库状态
flask db current

# Python交互式终端
flask shell
```

### Vue前端

```bash
# 运行开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

---

## 🐛 常见问题

### Q1: Flask无法连接数据库
**A**: 
1. 检查 `.env` 中的 `DATABASE_URL` 是否正确
2. 确保PlanetScale数据库已创建且在线
3. 检查网络连接

### Q2: Vue无法访问Flask API (CORS错误)
**A**:
1. 确保Flask中CORS配置正确
2. 检查 `.env` 中 `CORS_ORIGINS` 包含 `http://localhost:5173`
3. 重启Flask服务器

### Q3: npm install失败
**A**:
```bash
# 清除npm缓存
npm cache clean --force

# 删除node_modules和package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### Q4: Python依赖安装失败
**A**:
```bash
# 升级pip
pip install --upgrade pip

# 单独安装失败的包
pip install package-name

# 或使用conda（如果用Anaconda）
conda install package-name
```

---

## 📚 推荐学习资源

### Flask
- [Flask官方文档](https://flask.palletsprojects.com/)
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

### Vue 3
- [Vue官方教程](https://cn.vuejs.org/guide/quick-start.html)
- [Vue Mastery](https://www.vuemastery.com/)

### SQLAlchemy
- [SQLAlchemy文档](https://docs.sqlalchemy.org/)
- [Flask-SQLAlchemy快速入门](https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/)

---

## 💡 开发提示

1. **使用虚拟环境** - 始终在激活虚拟环境的情况下开发
2. **频繁测试** - 每完成一个小功能就测试
3. **Git提交** - 每完成一个功能就提交代码
4. **查阅文档** - 遇到问题先查官方文档
5. **使用AI助手** - Claude/ChatGPT可以帮助解决问题

---

## 🎯 第一周目标

到Week 1结束时，您应该能够：
- ✅ Flask后端运行正常
- ✅ 数据库连接成功
- ✅ 用户可以注册
- ✅ 用户可以登录
- ✅ JWT Token认证工作

**准备好开始了吗？从Week 1 Day 1开始！** 🚀
