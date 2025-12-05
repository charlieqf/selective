# 上线前准备工作清单 (Pre-Launch Checklist)

本文档详细列出了 Selective 项目上线前需要完成的基础设施准备、备份策略及安全检查工作。

## 1. 数据灾备机制 (Backup Strategy)

数据是系统的核心，必须确保在意外发生时（如误删、服务商故障）能够恢复。

### 1.1 数据库备份 (TiDB / PlanetScale)

虽然 PlanetScale 提供了高可用性，但为了防止人为操作失误（如误删表），必须持有离线备份。

*   **自动备份 (Daily Backups)**:
    *   登录 PlanetScale 控制台，确认已开启 "Daily scheduled backups"。
    *   *注意：免费版可能会有保留期限限制，请查阅当前套餐详情。*

*   **异地冷备份 (Offsite Backup)**:
    *   **方案**: 使用 `mysqldump` 定期导出 SQL 文件并存储在另一个云存储（如 AWS S3 或 阿里云 OSS）或本地 NAS 中。
    *   **操作脚本示例**:
        ```bash
        # 建议每周执行一次
        mysqldump -h <ps_host> -u <ps_user> -p<ps_password> --ssl-ca=/etc/ssl/certs/ca-certificates.crt --single-transaction --quick --lock-tables=false selective_db > selective_backup_$(date +%F).sql
        ```

### 1.2 多媒体资源备份 (Cloudinary)

Cloudinary 存储了所有的题目图片。

*   **官方备份**:
    *   登录 Cloudinary Console -> Settings -> Upload -> Backup。
    *   *注意：自动备份到 S3 通常是付费功能。*

*   **手动/脚本备份 (推荐)**:
    *   由于我们使用免费/低阶套餐，建议编写脚本调用 Cloudinary Admin API 获取所有资源列表并下载。
    *   **策略**: 编写一个 Python 脚本 `scripts/backup_cloudinary.py`。
    *   **逻辑**:
        1. 使用 `cloudinary.api.resources()` 获取所有图片 URL。
        2. 对比本地/备份桶中是否已存在。
        3. 下载新增图片。

## 2. 生产环境服务器准备 (Infrastructure)

根据您的技术栈 (Flask + Vue)，推荐以下两种部署方案。对于家庭/小范围试用，**方案 A (PaaS)** 成本最低且维护最简单。

### 方案 A: PaaS 托管 (推荐)

无需管理服务器操作系统，只需推送代码。

*   **前端 (Frontend)**: **Vercel**
    *   **准备**: 注册 Vercel 账号，绑定 GitHub 仓库。
    *   **配置**:
        *   Framework Preset: Vue.js
        *   Environment Variables: `VITE_API_URL` (填后端地址)
*   **后端 (Backend)**: **Railway** 或 **Render**
    *   **准备**: 注册账号。
    *   **配置**:
        *   Environment Variables: 填入 `DATABASE_URL`, `CLOUDINARY_*`, `SECRET_KEY`, `JWT_SECRET_KEY`。
        *   Start Command: `gunicorn -w 3 -b 0.0.0.0:$PORT run:app`
    *   **优点**: 自动配置 HTTPS，自动扩缩容，内置日志查看。

### 方案 B: 传统云服务器 (VPS)

如果您希望拥有完全的控制权（如安装特定软件、更低的长期计算成本）。

*   **选型**: AWS EC2 t3.micro / 阿里云 ECS突发性能型 / DigitalOcean / Vultr。
*   **规格**: 1 vCPU, 1GB RAM (最低配置)。
*   **操作系统**: Ubuntu 22.04 LTS 或 Debian 11。
*   **环境安装清单**:
    ```bash
    # 1. 基础环境
    sudo apt update && sudo apt install python3-pip python3-venv nginx git
    
    # 2. 从 GitHub 拉取代码
    git clone https://github.com/your/repo.git
    
    # 3. 后端运行 (Gunicorn + Systemd)
    # 需配置 /etc/systemd/system/selective.service
    
    # 4. 前端构建
    # 在本地 build 后上传 dist 目录，或在服务器安装 Node.js 进行 build
    
    # 5. Nginx 反向代理
    # 配置 Nginx 将 /api 转发给 Gunicorn (localhost:8000)，将 / 指向静态文件 index.html
    ```
*   **域名与 HTTPS**:
    *   购买域名。
    *   使用 `certbot --nginx` 自动申请并配置 Let's Encrypt 免费证书。

## 3. 其他必要准备工作 (Checklist)

### 3.1 安全性检查
- [ ] **SECURE SECRETS**: 确保生产环境的 `SECRET_KEY` 和 `JWT_SECRET_KEY` 是随机长字符串，**绝对不能**使用默认值。
- [ ] **DEBUG 关闭**: 生产环境确保 `FLASK_DEBUG=0` 或 `False`。
- [ ] **CORS 限制**: 将 `CORS_ORIGINS` 严格设置为您的前端域名（如 `https://selective-app.vercel.app`），不要留 `*`。

### 3.2 监控与日志
- [ ] **错误追踪**: 建议后端安装 **Sentry** SDK。
    *   `pip install sentry-sdk`
    *   在 `create_app` 中初始化。这样一旦报错，您会立即收到邮件通知，而不是等用户反馈。
- [ ] **服务监控**: 使用 **UptimeRobot** (免费) 每5分钟 ping 一下您的 API 接口，确保服务在线。

### 3.3 数据库连接池优化
- [ ] 在 `config.py` 的生产配置中，确保 SQLAlchemy 连接池设置合理：
    ```python
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,  # 这里的秒数要小于数据库的超时时间 (wait_timeout)
        'pool_pre_ping': True # 自动检测断开的连接
    }
    ```
    *TiDB/MySQL 通常 wait_timeout 较短，必须配置 `pool_recycle` 防止 "MySQL server has gone away" 错误。*

## 4. 应急预案 (Disaster Recovery)

*   **数据库故障**: 确认最近一份 `sql` 备份位置。如果是 PlanetScale 故障，暂无办法，只能等待恢复（SLA保障）。
*   **代码回滚**: 确保 Git 分支清晰，如发布出现严重 Bug，能在 Vercel/Railway 上一键 "Rollback" 到上一个 commit。
