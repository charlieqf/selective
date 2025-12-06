# Master Deployment Runbook (Execution Plan)

This document outlines the **linear execution steps** to deploy the `selective` application to production using the **PaaS Strategy (Railway + Vercel)**.

**Prerequisites**:
*   GitHub Repository updated with latest code.
*   Accounts detailed in `docs/18-paas-deployment-guide.md` (Railway, Vercel, TiDB, Cloudinary).

---

## Phase 1: Code Synchronization (Local Machine)

Before creating services, ensure your repository has the critical configuration changes we made.

1.  **Verify Configuration**:
    *   Check `backend/config.py`: Ensure `ProductionConfig` has `pool_recycle` set to **280**.
    *   Check `backend/Procfile`: Ensure it exists and contains `flask db upgrade`.
2.  **Commit & Push**:
    ```bash
    git add backend/config.py backend/Procfile docs/
    git commit -m "chore: Prepare for production deployment"
    git push origin main
    ```

---

## Phase 2: Infrastructure Provisioning

### 2.1 Database (TiDB Cloud)
1.  Login to TiDB Cloud.
2.  Create a **Serverless Tier** cluster.
3.  Go to "Connect" and generate a password.
4.  **Copy the Connection String**.
    *   Format: `mysql+pymysql://user:password@host:4000/db?ssl_mode=VERIFIED`
    *   *Tip: Ensure you append `?ssl_mode=VERIFIED` if it's not present.*

### 2.2 Storage (Cloudinary)
1.  Login to Cloudinary.
2.  Go to Dashboard.
3.  **Copy API Environment Variables**:
    *   `Cloud Name`
    *   `API Key`
    *   `API Secret`

### 2.3 Secret Generation
Generate random keys for your application security (run in your local terminal):
```bash
openssl rand -hex 32  # Use for SECRET_KEY
openssl rand -hex 32  # Use for JWT_SECRET_KEY
```

---

## Phase 3: Backend Deployment (Railway)

1.  **Create Project**: Dashboard -> New Project -> Deploy from My Repo -> `selective`.
2.  **Configure Root Directory**:
    *   Click the project card -> Settings -> **Source**.
    *   Click **"Add Root Directory"**.
    *   Enter: `backend` -> Save.
3.  **Add Environment Variables**:
    *   Click "Variables".
    *   Add `DATABASE_URL` (from Phase 2.1).
    *   Add `CLOUDINARY_URL` (Format: `cloudinary://<api_key>:<api_secret>@<cloud_name>`).
    *   Add `SECRET_KEY`, `JWT_SECRET_KEY` (from Phase 2.3).
    *   **Add `CORS_ORIGINS`**: Set to `http://localhost:5173` (Safe placeholder).
        *   **CRITICAL**: Do NOT use `*` in production, even temporarily.
        *   *Note: Frontend requests will fail with CORS errors until we update this in Phase 5.*
4.  **Deploy**:
    *   Railway should proactively trigger a build. Check "Deployments" tab.
    *   Verify "Build" logs show `requirements.txt` installing.
    *   Verify "Deploy" logs show `flask db upgrade` running successfully.
5.  **Get URL**:
    *   Settings -> Networking -> Public Networking -> Generate Domain.
    *   Copy the URL (e.g., `https://selective-prod.up.railway.app`).

---

## Phase 4: Frontend Deployment (Vercel)

1.  **Create Project**: Dashboard -> Add New -> Project -> `selective`.
2.  **Configure Build**:
    *   **Root Directory**: Click "Edit" -> Select `frontend`.
    *   **Framework Preset**: Vite.
3.  **Add Environment Variables**:
    *   Name: `VITE_API_URL`
    *   Value: Paste the **Railway URL** from Phase 3 (e.g., `https://selective-prod.up.railway.app`).
    *   Name: `VITE_CLOUDINARY_CLOUD_NAME`
    *   Value: Your Cloudinary Cloud Name (e.g., `dsrb7j7rm`).
4.  **Deploy**:
    *   Click "Deploy".
    *   Wait for the "Congratulations!" screen.
    *   Copy the Vercel Domain (e.g., `https://selective-app.vercel.app`).

---

## Phase 5: Security Hardening (Crucial)

Now that we have the frontend URL, we will allow it to access the backend.

1.  Return to **Railway Dashboard**.
2.  Go to "Variables".
3.  **Edit `CORS_ORIGINS`**:
    *   Change from `http://localhost:5173` to your **Vercel Domain** (e.g., `https://selective-app.vercel.app`).
    *   *Note: If you have a custom domain, add that too (comma separated).*
4.  Railway will automatically redeploy (Wait ~1-2 mins).

---

## Phase 6: Final Verification (Smoke Test)

1.  Open your Vercel App URL on a **Mobile Device** (Real device test).
2.  **Register a new user**. (This verifies Database writes).
3.  **Click "Create" -> "Take Photo"**.
    *   Verify browser asks for Camera permission. (Verifies HTTPS).
    *   Take a photo and upload. (Verifies Cloudinary).
4.  **Check Dashboard**.
    *   Verify the new question appears.

## Deployment Complete 🚀
