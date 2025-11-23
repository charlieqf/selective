# 技术栈版本规范

## 原则

- ✅ 使用**稳定版本**（非最新，但经过验证）
- ✅ 使用**LTS版本**（长期支持）
- ✅ 明确**主要版本**，次要版本灵活
- ✅ 定期更新（每3-6个月检查一次）

---

## 1. Python技术栈

### Python版本
```
推荐: Python 3.11.x
最低: Python 3.9+
原因:
  - Python 3.11性能提升25%
  - 稳定且广泛支持
  - Railway/Render默认支持
  - 2027年前持续维护
```

### Flask后端依赖（requirements.txt）

```txt
# requirements.txt

# ===== 核心框架 =====
Flask==3.0.0
Werkzeug==3.0.1

# ===== 数据库 =====
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.23
PyMySQL==1.1.0
cryptography==41.0.7  # PyMySQL需要

# ===== 数据库迁移 =====
Flask-Migrate==4.0.5
alembic==1.13.1

# ===== 认证 =====
Flask-JWT-Extended==4.6.0
PyJWT==2.8.0
bcrypt==4.1.2

# ===== API相关 =====
Flask-CORS==4.0.0
Flask-Marshmallow==0.15.0
marshmallow==3.20.1
marshmallow-sqlalchemy==0.29.0

# ===== 文件上传 =====
cloudinary==1.40.0

# ===== 环境配置 =====
python-dotenv==1.0.0

# ===== 生产服务器 =====
gunicorn==21.2.0

# ===== 开发工具 =====
pytest==7.4.3
pytest-flask==1.3.0
pytest-cov==4.1.0
black==23.12.1
flake8==6.1.0

# ===== 可选：数据验证 =====
email-validator==2.1.0.post1
```

**版本说明**：
- `Flask==3.0.0` - 最新稳定版，2023年发布
- `SQLAlchemy==2.0.23` - 2.0系列稳定版
- `Flask-JWT-Extended==4.6.0` - JWT认证标准库
- `cloudinary==1.40.0` - 最新稳定版

### Python版本管理

**检查Python版本**：
```powershell
python --version
# 应该是: Python 3.11.x 或 3.10.x
```

**如果版本不对**：
```powershell
# Windows: 下载安装
# https://www.python.org/downloads/

# 或使用pyenv-windows管理多版本
```

---

## 2. Node.js技术栈

### Node.js版本
```
推荐: Node.js 20.x LTS
最低: Node.js 18.x
原因:
  - LTS版本，维护到2026年
  - Vercel/Railway支持
  - Vite最佳性能
```

### Vue前端依赖（package.json）

```json
{
  "name": "selective-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.5",
    "naive-ui": "^2.38.0",
    "@vicons/ionicons5": "^0.12.0",
    "vee-validate": "^4.12.4",
    "yup": "^1.3.3",
    "date-fns": "^3.0.6",
    "echarts": "^5.4.3",
    "vue-echarts": "^6.6.7",
    "vuedraggable": "^4.1.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.2",
    "vite": "^5.0.11",
    "tailwindcss": "^3.4.1",
    "postcss": "^8.4.33",
    "autoprefixer": "^10.4.16"
  }
}
```

**版本说明**：
- `vue@^3.4.0` - Vue 3最新稳定版
- `vite@^5.0.11` - Vite 5，构建速度最快
- `naive-ui@^2.38.0` - Vue 3 UI库
- `pinia@^2.1.7` - Vue官方状态管理

### Node.js版本管理

**检查Node.js版本**：
```powershell
node --version
# 应该是: v20.x.x 或 v18.x.x

npm --version
# 应该是: 10.x.x+
```

**如果版本不对**：
```powershell
# Windows: 下载安装
# https://nodejs.org/

# 推荐下载20.x LTS版本
```

---

## 3. 数据库版本

### MySQL（PlanetScale）
```
版本: MySQL 8.0
说明: PlanetScale使用MySQL 8.0兼容协议
特性:
  - JSON字段支持
  - 更好的性能
  - 窗口函数
```

---

## 4. 云服务版本

### Cloudinary
```
SDK版本: cloudinary==1.40.0
API版本: v1_1（自动）
```

### PlanetScale
```
协议: MySQL 8.0
连接: mysql+pymysql://
```

---

## 5. 开发工具版本

### Git
```
推荐: Git 2.40+
最低: Git 2.30+
```

### Windsurf / VS Code
```
Windsurf: 最新版
VS Code: 1.85+（如果使用）
```

---

## 6. 版本锁定策略

### Python依赖
```txt
# requirements.txt 使用精确版本（推荐）
Flask==3.0.0

# 或使用兼容版本
Flask>=3.0.0,<4.0.0
```

**推荐**：MVP阶段用精确版本（`==`），生产稳定后再用兼容版本（`>=,<`）

### Node.js依赖
```json
{
  "dependencies": {
    "vue": "^3.4.0"  // 兼容3.4.x所有版本
  }
}
```

**`package-lock.json`**：
- ✅ 提交到Git
- ✅ 确保团队依赖一致
- ✅ 生产环境使用 `npm ci` 而非 `npm install`

---

## 7. 兼容性矩阵

### Python + Flask
| Python | Flask | SQLAlchemy | 状态 |
|--------|-------|------------|------|
| 3.11.x | 3.0.0 | 2.0.23 | ✅ 推荐 |
| 3.10.x | 3.0.0 | 2.0.23 | ✅ 支持 |
| 3.9.x  | 3.0.0 | 2.0.23 | ⚠️ 可用 |
| 3.8.x  | 3.0.0 | 2.0.23 | ❌ 不推荐 |

### Node.js + Vue
| Node.js | Vue | Vite | 状态 |
|---------|-----|------|------|
| 20.x LTS | 3.4.0 | 5.0.11 | ✅ 推荐 |
| 18.x LTS | 3.4.0 | 5.0.11 | ✅ 支持 |
| 16.x | 3.4.0 | 5.0.11 | ⚠️ 即将EOL |

---

## 8. 部署环境版本

### Railway
```yaml
Python Runtime: 3.11
Node Runtime: 20.x
自动检测: requirements.txt 或 package.json
```

### Vercel
```yaml
Node Runtime: 20.x
Build Command: npm run build
Output Directory: dist
```

---

## 9. 版本更新策略

### 何时更新

#### 立即更新（安全补丁）
```
cryptography: 发现CVE漏洞
PyJWT: 安全更新
```

#### 定期更新（功能更新）
```
每3个月: 检查依赖更新
每6个月: 主要版本升级评估
```

#### 不更新（稳定优先）
```
MVP阶段: 锁定版本
生产稳定后: 谨慎更新
```

### 更新流程

```bash
# 1. 检查过时的包
pip list --outdated
npm outdated

# 2. 在开发环境测试更新
pip install --upgrade package-name
npm update package-name

# 3. 运行测试
pytest
npm run test

# 4. 更新requirements.txt/package.json
pip freeze > requirements.txt
# package.json自动更新

# 5. 提交到Git
git commit -m "chore: update dependencies"

# 6. 部署到测试环境验证

# 7. 部署到生产环境
```

---

## 10. 常见问题

### Q: 我的Python版本是3.12，可以用吗？
A: 可以，但某些依赖可能未完全兼容。推荐3.11.x。

### Q: 必须用这些精确版本吗？
A: MVP阶段建议用精确版本避免问题。次要版本差异（如3.11.5 vs 3.11.7）通常没问题。

### Q: 如何在Windows上管理多个Python版本？
A: 使用pyenv-windows或直接安装特定版本到不同目录。

### Q: package.json中的^是什么意思？
A: `^3.4.0` 表示兼容 3.4.x 所有版本，但不包括 4.0.0。

### Q: 依赖冲突怎么办？
A: 
```bash
# Python
pip install pip-tools
pip-compile requirements.in

# Node.js
npm install --legacy-peer-deps
```

---

## 11. 完整环境检查清单

### 开发环境设置前检查
```powershell
# Python
python --version
# 期望: Python 3.11.x 或 3.10.x

# Node.js
node --version
# 期望: v20.x.x 或 v18.x.x

npm --version
# 期望: 10.x.x+

# Git
git --version
# 期望: 2.40+

# 检查PATH
where python
where node
where git
```

### 虚拟环境创建
```powershell
# 创建虚拟环境（使用系统Python版本）
python -m venv venv

# 激活
.\venv\Scripts\activate

# 验证虚拟环境中的Python版本
python --version
which python  # 应该指向venv目录
```

---

## 12. 总结

### ✅ 推荐配置

```
开发机器:
├── Python 3.11.x
├── Node.js 20.x LTS
├── Git 2.40+
└── Windsurf (最新版)

后端依赖:
├── Flask 3.0.0
├── SQLAlchemy 2.0.23
└── 见完整requirements.txt

前端依赖:
├── Vue 3.4.0
├── Vite 5.0.11
└── 见完整package.json

云服务:
├── PlanetScale (MySQL 8.0)
├── Cloudinary (latest)
├── Vercel (Node 20.x)
└── Railway (Python 3.11)
```

### 🎯 下一步

1. ✅ 确认Python和Node.js版本正确
2. ✅ 创建虚拟环境
3. ✅ 创建requirements.txt（我可以帮您创建）
4. ✅ 创建package.json（我可以帮您创建）
5. ✅ 安装依赖

**准备好了吗？我可以立即为您创建这些文件！** 🚀
