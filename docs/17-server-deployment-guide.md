# Server Deployment Guide (Low Resource Environments)

This guide is recommended for scenarios with **resource-constrained servers (e.g., 1GB RAM Ubuntu 22.04)** and **no custom domain**, ensuring that **Mobile Camera functionality (requires HTTPS)** remains available.

## Core Strategy

1.  **Solve HTTPS Issue**: Use **nip.io** (Wildcard DNS Service) + **Let's Encrypt**.
    *   *Principle*: If your IP is `1.2.3.4`, using the domain `1.2.3.4.nip.io` resolves back to `1.2.3.4`, allowing for legitimate SSL certificate issuance.
2.  **Solve Resource Constraints**: **Local Build, Remote Run**.
    *   **Crucial**: Never run `npm run build` on a 1GB RAM server; it will cause OOM errors.
    *   Build locally and only upload the generated `dist/` files.
3.  **Process Management**: Use **Systemd** + **Nginx** (Traditional architecture).

---

## 1. Local Preparation

### 1.1 Frontend Build
Execute on your development machine:
```bash
cd frontend
# 1. Update config to point to the server's nip.io domain
# Recommendation: Create .env.production
# VITE_API_URL=https://<YOUR_SERVER_IP>.nip.io/api

# 2. Build
npm run build

# 3. This generates the dist/ directory
```

### 1.2 Prepare Code Package
To save bandwidth, only upload necessary files.

---

## 2. Server Operations

Assuming Server IP is `XX.XX.XX.XX`.
Target Domain: `XX.XX.XX.XX.nip.io`

### 2.1 Install Base Environment
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx
```

### 2.2 Deploy Backend (Flask)

**1. Upload Code**: Upload `backend/` directory to `/var/www/selective/backend`.

**2. Python Environment**:
```bash
cd /var/www/selective/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn pymysql cryptography
```

**3. Configure Gunicorn Service (Systemd)**:
Create `/etc/systemd/system/selective.service`:
```ini
[Unit]
Description=Gunicorn instance to serve Selective App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/selective/backend
Environment="PATH=/var/www/selective/backend/venv/bin"
# Fill in your Config variables
Environment="DATABASE_URL=mysql+pymysql://..." 
Environment="SECRET_KEY=..."
Environment="JWT_SECRET_KEY=..."
Environment="CLOUDINARY_CLOUD_NAME=..."
Environment="CLOUDINARY_API_KEY=..."
Environment="CLOUDINARY_API_SECRET=..."
# CRITICAL: Limit workers to 2 (or 1) for low RAM environments
ExecStart=/var/www/selective/backend/venv/bin/gunicorn --workers 2 --bind 127.0.0.1:5000 run:app

[Install]
WantedBy=multi-user.target
```

**4. Initialize Database (Migration)**:
Before starting the service, run migrations to create tables.
```bash
# Ensure venv is active
export FLASK_APP=run.py
export DATABASE_URL="mysql+pymysql://..." # Same as above
flask db upgrade
```

**5. Start Backend**:
```bash
sudo systemctl start selective
sudo systemctl enable selective
```

### 2.3 Deploy Frontend (Static Files)

**1. Upload Files**: Upload local `dist/` directory contents to `/var/www/selective/frontend/dist`.

**2. Set Permissions**:
```bash
sudo chown -R www-data:www-data /var/www/selective
```

### 2.4 Configure Nginx & HTTPS

Create `/etc/nginx/sites-available/selective` (See template in full guide or Copy Nginx config blocks).
Ensure `server_name` matches your `nip.io` domain.

Enable HTTPS:
```bash
sudo certbot --nginx -d XX.XX.XX.XX.nip.io
```

---

## 3. Operations & Troubleshooting

### 3.1 Logs
*   **Backend Logs**: `sudo journalctl -u selective -f`
*   **Access Logs**: `sudo tail -f /var/log/nginx/access.log`
*   **Error Logs**: `sudo tail -f /var/log/nginx/error.log`

### 3.2 Health Check
Visit `https://XX.XX.XX.XX.nip.io/api/auth/me` (requires token) or check system status:
```bash
systemctl status selective
systemctl status nginx
```
