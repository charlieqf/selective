# Cloud Services Setup Guide

This guide details how to set up the cloud services required for the Selective Exam Platform: **TiDB Cloud** (Database) and **Cloudinary** (Image Storage).

## 1. Database: TiDB Cloud (MySQL Compatible)

We use TiDB Cloud Serverless because it offers a generous free tier and is fully compatible with MySQL.

### Setup Steps

1.  **Register**: Go to [TiDB Cloud](https://tidbcloud.com/) and sign up for a free account.
2.  **Create Cluster**:
    *   Click **"Create Cluster"**.
    *   Select **"Serverless"** tier (Free).
    *   Choose a region (e.g., AWS / Singapore or Tokyo).
    *   Give your cluster a name (e.g., `selective-dev`).
3.  **Get Connection String**:
    *   Once the cluster is ready, click **"Connect"**.
    *   In the "Connect with" dropdown, select **"SQLAlchemy"** (since we use Python/Flask).
    *   **Operating System**: Select your OS (Windows/Mac/Linux).
    *   **Generate Password**: Click "Generate Password" if prompted. **Copy this password immediately**, it won't be shown again.
    *   **Copy the URL**: You will see a URL starting with `mysql+pymysql://...`.

### Configuration

Update your `backend/.env` file:

```env
# Replace YOUR_PASSWORD with the generated password
# Note: We add ssl_verify_cert=true&ssl_verify_identity=true for security
DATABASE_URL=mysql+pymysql://<username>:<password>@<host>:4000/<database>?ssl_verify_cert=true&ssl_verify_identity=true
```

### Initialization

After configuring `.env`, initialize the database schema:

```bash
cd backend
flask db upgrade
```

---

## 2. Image Storage: Cloudinary

We use Cloudinary for storing and serving user-uploaded images (e.g., question screenshots).

### Setup Steps

1.  **Register**: Go to [Cloudinary](https://cloudinary.com/) and sign up for a free account.
2.  **Dashboard**: Log in to access your **Programmable Media** Dashboard.
3.  **Get Credentials**:
    *   Look for the **"Product Environment Credentials"** section (usually at the top left).
    *   Copy the following values:
        *   **Cloud Name**
        *   **API Key**
        *   **API Secret**

### Configuration

Update your `backend/.env` file:

```env
CLOUDINARY_CLOUD_NAME=<your_cloud_name>
CLOUDINARY_API_KEY=<your_api_key>
CLOUDINARY_API_SECRET=<your_api_secret>
```

### Verification

1.  Start the backend: `flask run`
2.  Start the frontend: `npm run dev`
3.  Go to `http://localhost:5173/questions/upload` and try uploading an image.
4.  If successful, the image is hosted on Cloudinary!

---

## Troubleshooting

### Database Connection Issues
*   **SSL Error**: Ensure `ssl_verify_cert=true` is in your connection string.
*   **Network**: Ensure your network allows outbound traffic to port 4000.
*   **Password**: If you forgot the password, you can reset it in the TiDB Cloud console under "Users".

### Image Upload Issues
*   **400 Bad Request**: Check if the file size exceeds 5MB.
*   **500 Internal Server Error**: Check backend logs. Usually indicates invalid Cloudinary credentials.
