# 开发、测试、生产环境配置指南

## 1. 环境架构建议

### ❌ 不推荐：自建Ubuntu服务器
**原因**：
- 需要自己管理服务器（更新、安全、备份）
- 需要配置Nginx、SSL证书、防火墙等
- 运维成本高，容易出问题
- 需要24/7运行，电费、网络成本

### ✅ 推荐：云平台托管（PaaS）
**优势**：
- 零运维：自动部署、自动扩展、自动备份
- 免费额度：足够MVP使用
- 专业团队维护安全和性能
- 全球CDN加速

---

## 2. 三个环境配置

### 2.1 开发环境（Local Development） - Windows 11

**您的本地机器（Windows 11）**

#### 后端（Flask）
```bash
# Windows 11 本地运行
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 运行开发服务器
flask run
# 访问: http://localhost:5000
```

#### 前端（Vue）
```bash
# Windows 11 本地运行
cd frontend
npm install
npm run dev
# 访问: http://localhost:5173
```

#### 数据库
- **选项A**：连接云端开发数据库（推荐）
  ```
  DATABASE_URL=mysql+pymysql://...@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/selective-dev
  ```
  - 优点：Windows不需要安装MySQL，**TiDB Cloud Serverless免费**
  - 缺点：需要网络连接
  - **详细配置请参考**: [Cloud Services Setup Guide](./cloud-services-setup.md)

- **选项B**：本地MySQL
  ```bash
  # Windows安装MySQL（不推荐，复杂）
  # 或使用Docker
  docker run -d -p 3306:3306 --name mysql -e MYSQL_ROOT_PASSWORD=password mysql:8
  ```

**推荐：选项A**（连接云端开发数据库）

#### 开发工具
```
VS Code（推荐）
  + Python扩展
  + Volar (Vue)扩展
  + Tailwind CSS扩展
  + SQLTools扩展（连接数据库）
```

#### 本地测试工作流
```
1. 修改代码（VS Code）
2. Flask自动重启（--debug模式）
3. Vue自动热更新（Vite HMR）
4. 浏览器自动刷新
5. 实时查看效果 ✅
```

---

### 2.2 测试环境（Staging） - 云端

**用途**：模拟生产环境，测试部署流程

#### 方案A：使用Git分支 + 云平台自动部署（推荐）

```
Git仓库分支:
├── main (生产)
├── develop (测试)
└── feature/* (功能开发)

云平台配置:
├── Production: 连接main分支
└── Staging: 连接develop分支
```

**Vercel配置（前端）**：
```yaml
# 自动部署
main分支 → https://selective.vercel.app (生产)
develop分支 → https://selective-dev.vercel.app (测试)
```

**Railway配置（后端）**：
```yaml
main分支 → https://api.selective.com (生产)
develop分支 → https://api-dev.selective.com (测试)
```

#### 方案B：专门的测试环境（可选）

使用Railway/Render的多环境功能：
```
Project: selective-backend
├── Production环境
│   └── DATABASE_URL: production数据库
└── Staging环境
    └── DATABASE_URL: staging数据库
```

**推荐：方案A**（Git分支自动部署，免费且简单）

---

### 2.3 生产环境（Production） - 云端

#### 前端：Vercel（推荐）
```
服务: Vercel
域名: https://selective-exam.vercel.app
     或 https://yourdomain.com (自定义域名)
特点:
  ✅ 全球CDN
  ✅ 自动HTTPS
  ✅ 自动部署（git push即可）
  ✅ 免费
```

#### 后端：Railway 或 Render（推荐）

**Railway**:
```
服务: Railway
URL: https://selective-backend.railway.app
特点:
  ✅ 免费$5/月额度
  ✅ 自动部署
  ✅ 自动HTTPS
  ✅ 简单易用
```

**Render**:
```
服务: Render
URL: https://selective-backend.onrender.com
特点:
  ✅ 完全免费（有15分钟冷启动）
  ✅ 自动HTTPS
  ✅ 简单配置
```

**推荐：Railway**（无冷启动，体验更好）

#### 数据库：TiDB Cloud Serverless (推荐)
```
服务: TiDB Cloud
特点:
  ✅ 永久免费 (5GB存储, 50M RU/月)
  ✅ MySQL高度兼容
  ✅ Serverless自动扩展
  ✅ 无需信用卡
```
*(PlanetScale已取消免费套餐，不再推荐)*

#### 文件存储：Cloudinary
```
服务: Cloudinary
特点:
  ✅ 免费25GB
  ✅ 自动CDN加速
  ✅ 图片自动优化
```

---

## 3. 完整环境对比表

| 环境 | 位置 | 访问方式 | 数据库 | 用途 |
|------|------|---------|--------|------|
| **开发** | Windows 11本地 | localhost:5173 | 云端dev数据库 | 日常开发 |
| **测试** | Vercel + Railway | xxx-dev.vercel.app | 云端staging数据库 | 部署前测试 |
| **生产** | Vercel + Railway | yourdomain.com | 云端prod数据库 | 真实用户使用 |

---

## 4. 本地开发详细指南（Windows 11）

### 4.1 安装必要软件

#### Python
```bash
# 下载Python 3.11+ from python.org
# 验证安装
python --version
pip --version
```

#### Node.js
```bash
# 下载Node.js 18+ from nodejs.org
# 验证安装
node --version
npm --version
```

#### Git
```bash
# 下载Git from git-scm.com
# 验证安装
git --version
```

#### Windsurf（推荐 - AI增强IDE）
```bash
# Windsurf是Codeium的AI代码编辑器
# 内置AI助手，编码效率更高

# 推荐扩展:
- Python（通常已内置）
- Volar（Vue开发）
- Tailwind CSS IntelliSense
- SQLTools（数据库管理）

# AI功能：
- Cascade模式：AI帮助编写代码
- Copilot++：智能代码补全
- 直接在编辑器内与AI对话
```

#### VS Code（备选）
```bash
# 下载from code.visualstudio.com
# 安装扩展:
- Python
- Volar
- Tailwind CSS IntelliSense
- SQLTools
```

### 4.2 项目设置（一次性）

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/selective-exam-platform.git
cd selective-exam-platform

# 2. 后端设置
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 创建.env文件
copy .env.example .env
# 编辑.env，填入PlanetScale等配置

# 数据库迁移
flask db upgrade

# 3. 前端设置
cd ..\frontend
npm install

# 创建.env文件
copy .env.example .env
# 编辑.env
```

### 4.3 日常开发工作流

```bash
# 终端1: 启动后端
cd backend
venv\Scripts\activate
flask run

# 终端2: 启动前端
cd frontend
npm run dev

# 浏览器访问: http://localhost:5173
```

**VS Code配置**：
```json
// .vscode/tasks.json - 一键启动所有服务
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Backend",
      "type": "shell",
      "command": "cd backend && venv\\Scripts\\activate && flask run",
      "isBackground": true
    },
    {
      "label": "Start Frontend",
      "type": "shell",
      "command": "cd frontend && npm run dev",
      "isBackground": true
    },
    {
      "label": "Start All",
      "dependsOn": ["Start Backend", "Start Frontend"]
    }
  ]
}
```

按`Ctrl+Shift+P` → `Run Task` → `Start All` 即可一键启动！

### 4.4 实时预览

**特性**：
- ✅ **Flask自动重启**：修改Python代码，Flask自动重启
- ✅ **Vue热更新**：修改Vue代码，浏览器自动更新（无需刷新）
- ✅ **Tailwind实时编译**：修改样式，立即生效

**体验**：
```
修改代码 → 保存 (Ctrl+S) → 浏览器自动更新 → 立即看到效果 🎉
```

---

## 5. 测试流程

### 5.1 本地测试（开发环境）

```bash
# 后端测试
cd backend
pytest

# 前端测试（可选）
cd frontend
npm run test

# 手动测试
# 打开浏览器，测试各个功能
```

### 5.2 部署到测试环境

```bash
# 1. 提交代码到develop分支
git checkout develop
git add .
git commit -m "Add feature X"
git push origin develop

# 2. 自动部署（Vercel + Railway自动检测）
# 几分钟后自动部署完成

# 3. 访问测试环境验证
# https://selective-dev.vercel.app
```

### 5.3 发布到生产环境

```bash
# 1. 合并到main分支
git checkout main
git merge develop
git push origin main

# 2. 自动部署到生产环境
# 几分钟后上线

# 3. 验证生产环境
# https://yourdomain.com
```

---

## 6. 环境变量管理

### 开发环境（本地）
```bash
# backend/.env
DATABASE_URL=mysql+pymysql://...@gateway01.ap-southeast-1.prod.aws.tidbcloud.com:4000/selective-dev
FLASK_ENV=development
FLASK_DEBUG=True
JWT_SECRET_KEY=dev-secret-key
CLOUDINARY_CLOUD_NAME=your-cloud
CORS_ORIGINS=http://localhost:5173

# frontend/.env
VITE_API_URL=http://localhost:5000
```

### 测试环境（云端）
```bash
# Railway环境变量（Staging）
DATABASE_URL=mysql+pymysql://...@aws.connect.psdb.cloud/selective-staging
FLASK_ENV=production
FLASK_DEBUG=False
JWT_SECRET_KEY=staging-secret-key-xxx
CORS_ORIGINS=https://selective-dev.vercel.app

# Vercel环境变量（Staging）
VITE_API_URL=https://api-dev.selective.railway.app
```

### 生产环境（云端）
```bash
# Railway环境变量（Production）
DATABASE_URL=mysql+pymysql://...@aws.connect.psdb.cloud/selective-prod
FLASK_ENV=production
FLASK_DEBUG=False
JWT_SECRET_KEY=<strong-random-key>
CORS_ORIGINS=https://yourdomain.com

# Vercel环境变量（Production）
VITE_API_URL=https://api.yourdomain.com
```

**关键**：每个环境使用不同的：
- 数据库（dev/staging/prod）
- 密钥（开发用简单的，生产用强密钥）
- CORS域名

---

## 7. 为什么不推荐Ubuntu自建服务器

### 对比

| 方面 | 云平台（推荐） | Ubuntu自建 |
|------|--------------|-----------|
| **初始设置** | 5分钟 | 2-4小时 |
| **月成本** | $0-20 | $10-50（服务器）+ 电费 + 网络 |
| **运维时间** | 0 | 每周2-5小时 |
| **安全更新** | 自动 | 需要手动 |
| **备份** | 自动 | 需要自己配置 |
| **扩展性** | 自动 | 需要手动升级服务器 |
| **SSL证书** | 自动（Let's Encrypt） | 需要配置 |
| **监控** | 内置 | 需要自己搭建 |
| **可靠性** | 99.9%+ | 取决于您的服务器 |

### 如果坚持要Ubuntu（不推荐）

如果您真的想自己部署：

```bash
# Ubuntu服务器配置（复杂！）
1. 购买VPS（DigitalOcean、AWS EC2等）
2. 安装Ubuntu 22.04
3. 安装Python、Node.js、Nginx、MySQL
4. 配置Nginx反向代理
5. 配置SSL证书（Let's Encrypt）
6. 配置防火墙（ufw）
7. 配置进程管理（supervisor/systemd）
8. 配置自动部署（GitHub Actions）
9. 配置监控（可选）
10. 配置备份（定期）

总时间: 4-8小时（首次）+ 持续维护
```

**强烈建议**：使用云平台，专注于开发产品，而非运维！

---

## 8. 推荐配置总结

### ✅ 最佳实践（推荐）

```
开发环境（本地Windows 11）:
├── Flask运行在 localhost:5000
├── Vue运行在 localhost:5173
└── 连接云端dev数据库

测试环境（云端）:
├── Vercel前端（develop分支自动部署）
├── Railway后端（develop分支自动部署）
└── TiDB Cloud Serverless数据库

生产环境（云端）:
├── Vercel前端（main分支自动部署）
├── Railway后端（main分支自动部署）
└── TiDB Cloud Serverless数据库

存储:
└── Cloudinary（所有环境共用）
```

### 成本估算

| 环境 | 月成本 |
|------|--------|
| 开发 | $0（本地） |
| 测试 | $0（免费额度） |
| 生产（小规模） | $0-30 |
| **总计** | **$0-30/月** |

对比自建Ubuntu服务器：$50-100/月 + 运维时间

---

## 9. 快速开始命令

### 首次设置（Windows 11）
```powershell
# 1. 安装软件
# - Python 3.11+
# - Node.js 18+
# - Git
# - VS Code

# 2. 克隆项目
git clone <repo-url>
cd selective-exam-platform

# 3. 后端设置
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade

# 4. 前端设置
cd ..\frontend
npm install

# 5. 启动开发服务器（两个终端）
# 终端1: cd backend && .\venv\Scripts\activate && flask run
# 终端2: cd frontend && npm run dev

# 6. 打开浏览器
# http://localhost:5173
```

### 日常开发
```powershell
# 启动（推荐使用VS Code任务）
Ctrl+Shift+P → Run Task → Start All

# 或手动启动两个终端
```

---

## 总结

**您的情况**：
- ✅ 本地开发：Windows 11完全OK，无需Linux
- ✅ 测试：云端自动部署，无需自建服务器
- ✅ 生产：云端托管，无需Ubuntu服务器
- ✅ 实时预览：Flask + Vite自动更新，开发体验极佳

**不需要Ubuntu服务器！**使用云平台更简单、更便宜、更可靠！ 🎉
