# 🚀 快速启动指南

## 当前项目状态

✅ 后端基础文件已创建
⏳ 前端待创建
⏳ 数据库待配置

---

## 立即开始（3个步骤）

### Step 1: 后端设置（5分钟）

```powershell
# 在Windsurf终端执行

# 1. 进入backend目录
cd c:\work\me\selective\backend

# 2. 创建Python虚拟环境
python -m venv venv

# 3. 激活虚拟环境
.\venv\Scripts\activate

# 4. 安装依赖（需要3-5分钟）
pip install -r requirements.txt

# 5. 创建.env文件
copy .env.example .env

# 6. 用记事本编辑.env（暂时可以跳过，使用默认值）
# notepad .env
```

**现在测试运行**：
```powershell
# 运行Flask（即使没有数据库也能运行）
flask run

# 应该看到:
# * Running on http://127.0.0.1:5000
```

打开浏览器访问 `http://localhost:5000`，应该看到：
```json
{
  "message": "NSW Selective School Exam Platform API",
  "version": "0.1.0",
  "status": "development"
}
```

✅ **如果看到这个，后端就成功了！**

---

### Step 2: 前端设置（5分钟）

```powershell
# 新开一个终端（保持Flask运行）

# 1. 回到项目根目录
cd c:\work\me\selective

# 2. 创建Vue项目
npm create vite@latest frontend -- --template vue

# 3. 进入frontend目录
cd frontend

# 4. 安装依赖（需要2-3分钟）
npm install

# 5. 运行开发服务器
npm run dev

# 应该看到:
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
```

打开浏览器访问 `http://localhost:5173`，应该看到Vue欢迎页面。

✅ **如果看到Vue页面，前端就成功了！**

---

### Step 3: 验证前后端通信（1分钟）

前端Vue页面中，打开浏览器控制台（F12），运行：

```javascript
fetch('http://localhost:5000/health')
  .then(r => r.json())
  .then(data => console.log(data))
```

如果看到：
```json
{
  "status": "ok",
  "message": "Server is running"
}
```

✅ **恭喜！前后端已联通！** 🎉

---

## 当前可以访问的URL

### 后端
- http://localhost:5000/ - API首页
- http://localhost:5000/health - 健康检查

### 前端
- http://localhost:5173/ - Vue应用

---

## 下一步（Week 1开发）

现在您有了一个可运行的基础项目，接下来按Week 1计划开发：

### Day 1-2: 数据库设置
1. 注册PlanetScale账号
2. 创建开发数据库
3. 更新.env中的DATABASE_URL
4. 初始化数据库迁移

### Day 3-4: 用户模型
1. 创建User模型
2. 创建数据库迁移
3. 测试数据库连接

### Day 5-7: 认证API
1. 注册API
2. 登录API
3. JWT Token验证

---

## 常见问题

### Q: pip install失败
```powershell
# 升级pip
python -m pip install --upgrade pip

# 重试
pip install -r requirements.txt
```

### Q: npm install失败
```powershell
# 清除缓存
npm cache clean --force

# 重试
npm install
```

### Q: 端口被占用
```powershell
# 后端改用5001端口
flask run --port 5001

# 前端改用3000端口
npm run dev -- --port 3000
```

### Q: 如何停止服务器
```powershell
# Ctrl+C 停止当前运行的服务器
```

---

## 项目结构（当前）

```
c:\work\me\selective\
├── backend\                      ✅ 已创建
│   ├── app\
│   │   └── __init__.py          ✅ Flask应用工厂
│   ├── venv\                    ⏳ 待创建（运行python -m venv venv）
│   ├── .env                     ⏳ 待创建（copy .env.example .env）
│   ├── .env.example             ✅ 环境变量模板
│   ├── .gitignore               ✅ Git忽略文件
│   ├── config.py                ✅ Flask配置
│   ├── requirements.txt         ✅ Python依赖
│   └── run.py                   ✅ 启动文件
│
├── frontend\                    ⏳ 待创建（npm create vite）
│
└── docs\                        ✅ 完整文档
```

---

## 检查清单

- [ ] Python虚拟环境已创建
- [ ] 后端依赖已安装
- [ ] Flask可以运行
- [ ] 浏览器能访问 localhost:5000
- [ ] Vue项目已创建
- [ ] 前端依赖已安装
- [ ] Vite可以运行
- [ ] 浏览器能访问 localhost:5173
- [ ] 前后端可以通信

**完成以上后，您就有了一个完整的开发环境！** 🚀
