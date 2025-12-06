# Serverless / PaaS Deployment Guide (NoOps)

This is the recommended approach for **avoiding server management** entirely.

## Architecture

*   **Frontend**: Vercel (Hosting static Vue pages, Global CDN)
*   **Backend**: Railway (Hosting Python Flask application container)
*   **Database**: TiDB Cloud (Serverless MySQL)
*   **Images**: Cloudinary

---

## 1. Backend Deployment (Railway)

### 1.1 Preparation (Procfile)
We have added a `Procfile` to the `backend/` directory. This ensures that:
1.  Database migrations (`flask db upgrade`) run automatically before the app starts.
2.  The start command is version-controlled.
*   **Content**: `web: flask db upgrade && gunicorn -w 2 -b 0.0.0.0:$PORT run:app`

### 1.2 Deployment Steps
1.  **Register**: Visit [railway.app](https://railway.app/).
2.  **New Project**: Deploy from your GitHub repository `selective`.
3.  **Configure Root Directory (Critical)**:
    Since this is a monorepo, you must tell Railway where the Python app lives.
    *   Go to "Settings" -> "General" -> "Root Directory".
    *   Enter: `backend`
    *   *This is required for Railway to find `requirements.txt` and `Procfile`.*
4.  **Configure Variables**:
    Add all backend environment variables listed in `docs/16-launch-preparation.md`.
    *   `DATABASE_URL`
    *   `CLOUDINARY_*` keys
    *   `SECRET_KEY`, `JWT_SECRET_KEY`
    *   `CORS_ORIGINS`: **Important**: Set this to your specific Vercel domain (e.g., `https://selective-app.vercel.app`). **Do not use `*` in production.**
5.  **Verify Start Command**:
    Railway should automatically detect the `Procfile` inside the `backend` folder. You do **not** need to manually configure the start command in the UI.
6.  **Generate Domain**:
    In "Settings" -> "Networking", generate your backend URL (e.g., `https://selective-production.up.railway.app`).

### 1.3 Critical Railway Considerations
*   **Region Selection**: Choose a Railway region (e.g., US West) that is physically close to your TiDB Cloud region to minimize database latency.
*   **Trial & Credit Burn**: The $5 trial credit consumes rapidly if you have multiple active services. Monitor usage to avoid surprise shutdowns.
*   **Cold Starts**: If you are on a free/trial plan, the container may "sleep" after inactivity, causing a 5-10 second delay for the first request.

---

## 2. Frontend Deployment (Vercel)

1.  **New Project**: Import `selective` repository on Vercel.
2.  **Build Settings**: Set Root Directory to `frontend`.
3.  **Environment Variables**:
    *   `VITE_API_URL`: Enter your Railway backend URL (e.g., `https://selective-production.up.railway.app`).
4.  **Deploy**: Verification should pass immediately.

---

## 3. Final Connection & Verification

1.  **Update CORS**: Once Vercel generates your final domain (e.g., `https://selective-tau.vercel.app`), go back to **Railway Variables** and update `CORS_ORIGINS` to this exact value.
2.  **Redeploy**: Railway will restart.
3.  **Verify Migrations**: Check Railway "Deploy Logs". You should see `flask db upgrade` running successful migrations before Gunicorn starts.
4.  **Functional Test**: Use the app to register/login.
