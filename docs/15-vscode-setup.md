# VS Code 配置指南

## 必装插件（Essential）

### 1. Python开发 ⭐⭐⭐
```
插件ID: ms-python.python
名称: Python
作用: Python语言支持、调试、智能感知
```

```
插件ID: ms-python.vscode-pylance
名称: Pylance
作用: 快速的Python类型检查和智能补全
```

```
插件ID: ms-python.black-formatter
名称: Black Formatter
作用: Python代码自动格式化
```

### 2. Vue/前端开发 ⭐⭐⭐
```
插件ID: vue.volar
名称: Vue - Official
作用: Vue 3官方插件，必装！
```

```
插件ID: bradlc.vscode-tailwindcss
名称: Tailwind CSS IntelliSense
作用: Tailwind类名自动补全和预览
```

### 3. 数据库 ⭐⭐⭐
```
插件ID: mtxr.sqltools
名称: SQLTools
作用: 数据库管理和查询
```

```
插件ID: mtxr.sqltools-driver-mysql
名称: SQLTools MySQL/MariaDB
作用: MySQL连接驱动（配合SQLTools使用）
```

---

## 推荐插件（Recommended）

### 4. Git增强 ⭐⭐
```
插件ID: eamodio.gitlens
名称: GitLens
作用: Git增强工具，查看代码历史、作者等
```

```
插件ID: mhutchie.git-graph
名称: Git Graph
作用: 可视化Git提交历史
```

### 5. 开发效率 ⭐⭐
```
插件ID: mikestead.dotenv
名称: DotENV
作用: .env文件语法高亮
```

```
插件ID: humao.rest-client
名称: REST Client
作用: 在VS Code内测试API（替代Postman）
```

```
插件ID: usernamehw.errorlens
名称: Error Lens
作用: 行内显示错误和警告
```

```
插件ID: christian-kohler.path-intellisense
名称: Path Intellisense
作用: 文件路径自动补全
```

### 6. 代码质量 ⭐
```
插件ID: streetsidesoftware.code-spell-checker
名称: Code Spell Checker
作用: 拼写检查
```

```
插件ID: dbaeumer.vscode-eslint
名称: ESLint
作用: JavaScript/Vue代码检查
```

```
插件ID: esbenp.prettier-vscode
名称: Prettier
作用: 代码格式化（前端）
```

---

## 安装方法

### 方法1: VS Code扩展市场（推荐）
1. 打开VS Code
2. 点击左侧「扩展」图标（Ctrl+Shift+X）
3. 搜索插件名称（如"Python"）
4. 点击「安装」

### 方法2: 命令行批量安装
```powershell
# 复制以下命令到终端一次性安装所有插件

# Python
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.black-formatter

# Vue/前端
code --install-extension vue.volar
code --install-extension bradlc.vscode-tailwindcss

# 数据库
code --install-extension mtxr.sqltools
code --install-extension mtxr.sqltools-driver-mysql

# Git
code --install-extension eamodio.gitlens
code --install-extension mhutchie.git-graph

# 效率工具
code --install-extension mikestead.dotenv
code --install-extension humao.rest-client
code --install-extension usernamehw.errorlens
code --install-extension christian-kohler.path-intellisense

# 代码质量
code --install-extension streetsidesoftware.code-spell-checker
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
```

---

## VS Code项目设置

### 创建 `.vscode/settings.json`
在项目根目录创建此文件：

```json
{
  // Python设置
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/Scripts/python.exe",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackPath": "${workspaceFolder}/backend/venv/Scripts/black.exe",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  
  // Vue/JavaScript设置
  "[vue]": {
    "editor.defaultFormatter": "vue.volar"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  
  // Tailwind设置
  "tailwindCSS.includeLanguages": {
    "vue": "html"
  },
  "tailwindCSS.experimental.classRegex": [
    ["class:\\s*?[\"'`]([^\"'`]*).*?[\"'`]", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ],
  
  // 文件关联
  "files.associations": {
    "*.env*": "dotenv",
    ".env.example": "dotenv"
  },
  
  // 排除文件
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/node_modules": true,
    "**/venv": true,
    "**/.pytest_cache": true
  },
  
  // 编辑器设置
  "editor.formatOnSave": true,
  "editor.tabSize": 4,
  "editor.rulers": [88, 120],
  "files.trimTrailingWhitespace": true,
  "files.insertFinalNewline": true
}
```

### 创建 `.vscode/launch.json`（调试配置）

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Flask: Backend",
      "type": "python",
      "request": "launch",
      "module": "flask",
      "env": {
        "FLASK_APP": "run.py",
        "FLASK_ENV": "development",
        "FLASK_DEBUG": "1"
      },
      "args": ["run", "--no-debugger", "--no-reload"],
      "jinja": true,
      "cwd": "${workspaceFolder}/backend"
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

### 创建 `.vscode/tasks.json`（任务配置）

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Backend",
      "type": "shell",
      "command": "${workspaceFolder}/backend/venv/Scripts/python.exe",
      "args": ["-m", "flask", "run"],
      "options": {
        "cwd": "${workspaceFolder}/backend",
        "env": {
          "FLASK_APP": "run.py",
          "FLASK_ENV": "development"
        }
      },
      "isBackground": true,
      "problemMatcher": {
        "pattern": {
          "regexp": ".",
          "file": 1,
          "location": 2,
          "message": 3
        },
        "background": {
          "activeOnStart": true,
          "beginsPattern": ".*",
          "endsPattern": "Running on.*"
        }
      }
    },
    {
      "label": "Start Frontend",
      "type": "shell",
      "command": "npm",
      "args": ["run", "dev"],
      "options": {
        "cwd": "${workspaceFolder}/frontend"
      },
      "isBackground": true,
      "problemMatcher": {
        "pattern": {
          "regexp": ".",
          "file": 1,
          "location": 2,
          "message": 3
        },
        "background": {
          "activeOnStart": true,
          "beginsPattern": ".*",
          "endsPattern": "Local:.*"
        }
      }
    },
    {
      "label": "Start All",
      "dependsOn": ["Start Backend", "Start Frontend"],
      "problemMatcher": []
    }
  ]
}
```

---

## SQLTools数据库连接配置

### 连接PlanetScale（开发数据库）

1. 安装SQLTools和MySQL驱动插件
2. 点击左侧「SQLTools」图标
3. 点击「Add New Connection」
4. 选择「MySQL」
5. 填写配置：

```
Connection name: PlanetScale Dev
Server: aws.connect.psdb.cloud
Port: 3306
Database: selective-dev
Username: [从PlanetScale复制]
Password: [从PlanetScale复制]
SSL: Use SSL
```

---

## 使用技巧

### 1. 一键启动所有服务
按 `Ctrl+Shift+P` → 输入 `Run Task` → 选择 `Start All`

自动启动Flask和Vue开发服务器！

### 2. 调试Flask
1. 设置断点（点击行号左侧）
2. 按 `F5` → 选择 `Flask: Backend`
3. 访问API，代码在断点处暂停

### 3. 格式化代码
- Python: 保存时自动格式化（Black）
- Vue: 保存时自动格式化（Volar）
- 手动格式化: `Shift+Alt+F`

### 4. 测试API（REST Client）
创建 `test-api.http` 文件：

```http
### 健康检查
GET http://localhost:5000/health

### 注册用户
POST http://localhost:5000/api/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "password123",
  "name": "Test User"
}
```

点击「Send Request」即可测试！

### 5. Git可视化
- 查看文件历史: 右键文件 → `GitLens: Open File History`
- 查看提交图: `Ctrl+Shift+P` → `Git Graph: View Git Graph`

---

## 快捷键推荐

```
Ctrl+Shift+P    命令面板
Ctrl+P          快速打开文件
Ctrl+Shift+F    全局搜索
Ctrl+`          打开终端
F5              启动调试
Shift+Alt+F     格式化代码
Ctrl+Shift+X    扩展市场
Ctrl+B          切换侧边栏
```

---

## 扩展优先级总结

### ⭐⭐⭐ 必装（立即安装）
- Python
- Pylance
- Vue - Official
- Tailwind CSS IntelliSense
- SQLTools + MySQL Driver

### ⭐⭐ 强烈推荐（提升效率）
- Black Formatter
- GitLens
- Error Lens
- REST Client
- DotENV

### ⭐ 可选（锦上添花）
- Git Graph
- Code Spell Checker
- ESLint
- Prettier

---

## 常见问题

### Q: Python插件找不到解释器？
A: 
1. 确保已创建虚拟环境: `python -m venv venv`
2. `Ctrl+Shift+P` → `Python: Select Interpreter`
3. 选择 `./backend/venv/Scripts/python.exe`

### Q: Volar和Vetur冲突？
A: 
- 只安装Volar（Vue 3官方）
- 如果已装Vetur，禁用或卸载它

### Q: Tailwind CSS不提示？
A: 
- 确保frontend目录有 `tailwind.config.js`
- 重启VS Code

### Q: 如何禁用某个插件的格式化？
A: 
在settings.json中：
```json
"[python]": {
  "editor.formatOnSave": false
}
```

---

**现在您可以开始安装插件了！建议先安装必装的5个，之后根据需要添加其他插件。** 🚀
