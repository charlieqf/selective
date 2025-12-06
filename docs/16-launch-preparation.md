# Pre-Launch Checklist

This document is tailored for the **TiDB Cloud + Cloudinary + Flask + Vue** stack. Please review each item before launch.

## 1. Infrastructure Preparation

### 1.1 Environment Variables

Ensure your production environment (Railway/Render) has the following variables configured. These are extracted directly from `backend/config.py`.

| Variable Name | Required | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Yes | TiDB Cloud Connection String (Must include `?ssl_mode=VERIFIED`) | `mysql+pymysql://user:pass@gateway01.us-west-2.prod.aws.tidbcloud.com:4000/db?ssl_mode=VERIFIED` |
| `SECRET_KEY` | Yes | Flask Session Encryption Key (Random generated) | `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | Yes | JWT Signing Key (Random generated) | `openssl rand -hex 32` |
| `CLOUDINARY_URL` | Yes | Cloudinary Connection URL | `cloudinary://12345:abcde@my-app` |
| `CORS_ORIGINS` | Yes | Allowed Frontend Domains (Comma separated) | `https://your-frontend.vercel.app` |
| `FLASK_DEBUG` | No | Must be disabled in production | `0` or `False` |

### 1.2 Frontend Build Configuration (Vercel)

When deploying the frontend on Vercel, configure only one variable:

| Variable Name | Description |
| :--- | :--- |
| `VITE_API_URL` | Backend API URL (e.g., `https://your-backend.railway.app`) |
| `VITE_CLOUDINARY_CLOUD_NAME` | Cloudinary Cloud Name (e.g., `dsrb7j7rm`) |

## 2. Database & Schema Management

### 2.1 Run Migrations (Critical)

**Before** the application starts serving traffic, the database schema must be up to date.
*   **Command**: `flask db upgrade`
*   **Timing**: Run this during the build phase or as part of the startup command.
*   *Note: In the provided PaaS configuration, we have included this in the `Procfile`.*

### 2.2 Backup Strategy (TiDB Cloud)

Since the Serverless Tier has limited automated backup capabilities, it is highly recommended to configure **Local/Offsite Cold Backups**.

*   **Manual Backup Script (mysqldump)**
    TiDB enforces strict TLS connections. Use `VERIFY_IDENTITY` to match the connection string security level.

    ```bash
    # Export Command
    # Note: TiDB port is typically 4000
    mysqldump -h <tidb-host> -P 4000 -u <tidb-user> -p<tidb-password> --ssl-mode=VERIFY_IDENTITY --single-transaction --quick --lock-tables=false --no-tablespaces selective_db > backup_$(date +%F).sql
    ```
    *Note: You may need to provide the CA bundle path if your system does not trust the TiDB certificate root by default.*

### 2.3 Cloudinary Resource Backup
*   **Backup Plan**: Script usage of the Admin API to fetch all resource URLs and save them to a local list.
    ```python
    import cloudinary.api
    resources = cloudinary.api.resources(type="upload", max_results=500)
    print(resources)
    ```

## 3. Production Checks

### 3.1 Connection Pool
TiDB Cloud (Serverless) has specific idle connection behaviors.
**Checkpoint**: Verify `pool_recycle` in `backend/config.py`.
*   Current Status: **Updated to 280 seconds** in `ProductionConfig`.
*   **Result**: Prevention of "MySQL server has gone away" errors.

### 3.2 Temporary File Cleanup
*   **Optimization**: Consider using a standalone Cron Job to invoke cleanup logic instead of synchronous execution during HTTP requests.

### 3.3 Security
*   **HTTPS**: Production frontend and backend **must** use HTTPS.
*   **SQLAlchemy Track Modifications**: Ensure this is set to `False`. (Current Value: `False` ✅)

## 4. Emergency Response

1.  **Frontend Unreachable**: Check Vercel Deployment Logs.
2.  **API 500 Error**: Check Railway/Render Backend Logs.
3.  **Database Connection Failure**: Login to TiDB Cloud Console to check cluster status.
4.  **Image Load Failure**: Check Cloudinary traffic quota.
