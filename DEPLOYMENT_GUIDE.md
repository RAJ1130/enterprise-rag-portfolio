# 🚀 Complete Deployment Guide: Render (Backend) & Vercel (Frontend)

This guide provides the exact steps to deploy the **Enterprise RAG & Knowledge Base** portfolio project online using **Render** for the Python/FastAPI backend and **Vercel** for the React frontend.

---

## 📂 Step 1: Push Project to GitHub

1. Create a new public or private repository on [GitHub](https://github.com/new), named `enterprise-rag` or `mummalar-portfolio-rag`.
2. Open your terminal in `C:\Users\ELCOT\.gemini\antigravity\scratch\enterprise-rag` and run:

```bash
git init
git add .
git commit -m "Initial commit: Enterprise RAG with Mummalar Raj portfolio integration"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

---

## 🖥️ Step 2: Deploy Backend on Render (Free)

Render hosts the FastAPI backend, hybrid vector database, and document processing.

1. Sign up / Log in to [render.com](https://render.com) using your GitHub account.
2. In the Render Dashboard, click **New +** → **Web Service**.
3. Select your GitHub repository (`enterprise-rag`).
4. Configure the service settings:
   - **Name**: `mummalar-rag-backend`
   - **Region**: Singapore / Frankfurt / Oregon (any closest)
   - **Runtime**: **Python 3**
   - **Build Command**:
     ```bash
     pip install -r backend/requirements.txt
     ```
   - **Start Command**:
     ```bash
     python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Plan**: **Free**
5. *(Optional)* Add Environment Variables under **Advanced**:
   - `LLM_PROVIDER`: `gemini` (or `local_simulated`)
   - `GEMINI_API_KEY`: *(Your Google Gemini API Key if you want live cloud generation)*
6. Click **Create Web Service**.
7. Render will build and deploy the backend. Copy your live backend URL:
   - Example: `https://mummalar-rag-backend.onrender.com`

---

## ⚡ Step 3: Deploy Frontend on Vercel (Free)

Vercel provides edge CDN hosting with instant SSL for your React UI.

1. Sign up / Log in to [vercel.com](https://vercel.com) using your GitHub account.
2. Click **Add New...** → **Project**.
3. Import your GitHub repository (`enterprise-rag`).
4. In the configuration screen:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click *Edit* and select **`frontend`**
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Expand **Environment Variables**:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://mummalar-rag-backend.onrender.com` *(paste your Render backend URL from Step 2)*
6. Click **Deploy**.
7. In ~45 seconds, Vercel will deploy your site with a permanent custom domain:
   - Example: `https://mummalar-rag-portfolio.vercel.app`

---

## 🎯 Option 4: Deploy Both Frontend + Backend in 1-Click on Render

If you prefer a **single live URL** (without configuring two separate dashboards):
1. In Render, select **New +** → **Blueprint**.
2. Connect your GitHub repo. Render will automatically read [`render.yaml`](./render.yaml).
3. Render builds both the React frontend and runs the FastAPI backend together at a single URL!

---

## 👤 Portfolio & Resume Showcase Features

Your live deployment now includes:
- **Interactive Resume Q&A**: Recruiters can ask the AI questions about your B.Tech education at Mahendra College of Engineering (CGPA 7.4), your internship at BDreamz Global Solutions, your skills in React/Django/FastAPI, and your projects (Crypto Tracker, Smart Health System).
- **Clickable Source Citations**: Every claim quotes `Mummalar_Raj_Resume.pdf` or `Mummalar_Raj_Resume.md` with page numbers and relevance scores.
- **Header Profile Button**: Clicking **"Resume / Profile"** in the top navigation bar opens your full interactive contact card with links to LinkedIn, Email, Phone, and Project summaries.
