# Deployment Guide: Django on Render + Express on Vercel

## Overview

Your project consists of two apps:
1. **Django Admin** (`Afronative_admin_sites`) → Deploy on **Render** (with Neon Postgres database)
2. **Express Website** (`Afro_Naitive`) → Deploy on **Vercel**

Both communicate via a JSON API protected by a shared `SITE_API_KEY`.

---

## Current State of Your Projects

| Check | Django Admin | Express Website |
|-------|:---:|:---:|
| Production-ready code | ✅ | ✅ |
| `.gitignore` configured | ✅ | ✅ |
| Pushed to GitHub | ❌ Not yet | ✅ Already pushed |
| `requirements.txt` | ❌ Missing | N/A |
| `Procfile` (Render needs this) | ❌ Missing | N/A |
| `vercel.json` (Vercel needs this) | N/A | ❌ Missing |

---

## Step 1: Prepare the Django Admin Project

### 1.1 Create `requirements.txt`

Create a file called `requirements.txt` in `C:\Users\SHARP\Desktop\Afronative_admin_sites\`:

```
Django>=4.2
cloudinary
django-cloudinary-storage
python-dotenv
dj-database-url
gunicorn
whitenoise
psycopg2-binary
Pillow
```

### 1.2 Create `Procfile`

Create a file called `Procfile` (no extension) in `C:\Users\SHARP\Desktop\Afronative_admin_sites\`:

```
web: gunicorn afronative.wsgi:application --bind 0.0.0.0:$PORT
```

This tells Render how to start your Django app with Gunicorn (production server).

### 1.3 Push Django to GitHub

**Create a Repository on GitHub:**

1. Go to [github.com](https://github.com) and sign in
2. Click the **+** icon (top right) → **New repository**
3. Fill in:
   - **Repository name**: `afronative-admin`
   - **Description**: "Django admin panel for AfroNative events website"
   - **Visibility**: Private (recommended) or Public
   - **DO NOT** check "Initialize with README"
4. Click **Create repository**

**Push Your Code from PowerShell:**

```powershell
cd C:\Users\SHARP\Desktop\Afronative_admin_sites

git init

git add .

git commit -m "Initial commit: Django admin for AfroNative"

git branch -M main

git remote add origin https://github.com/YOUR_USERNAME/afronative-admin.git

git push -u origin main
```

**Replace** `YOUR_USERNAME` with your actual GitHub username.

> Your `.gitignore` already excludes `.env`, `db.sqlite3`, `venv/`, and other sensitive files — nothing secret will be pushed ✅

---

## Step 2: Set Up the Postgres Database (Neon)

1. Go to [neon.tech](https://neon.tech) and sign up (free)
2. Create a new project called `afronative-admin`
3. Neon will give you a **connection string** like:

```
postgresql://user:password@ep-cool-dynamic-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

4. **Copy this connection string** — you'll need it in the next step

---

## Step 3: Deploy Django on Render

### 3.1 Create a Web Service

1. Go to your [Render dashboard](https://dashboard.render.com/) and sign up (free with GitHub)
2. Click **New +** → **Web Service**
3. Connect your GitHub repo (`afronative-admin`)
4. Fill in:

| Field | Value |
|-------|-------|
| Name | `afronative-admin` |
| Region | Choose closest to you (e.g., Frankfurt) |
| Branch | `main` |
| Root Directory | Leave blank |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn afronative.wsgi:application --bind 0.0.0.0:$PORT` |
| Type | **Free** |

### 3.2 Set Environment Variables

In the **Environment Variables** section, add:

| Name | Value |
|------|-------|
| `SECRET_KEY` | Run: `python -c "import secrets; print(secrets.token_urlsafe(50))"` and paste the output |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `afronative-admin.onrender.com` |
| `DATABASE_URL` | Paste your Neon connection string from Step 2 |
| `CLOUDINARY_URL` | `cloudinary://API_KEY:API_SECRET@Afro_native` (from your Cloudinary dashboard) |
| `SITE_API_KEY` | Run: `python -c "import secrets; print(secrets.token_urlsafe(32))"` and paste the output — **save this key, you'll need it for Vercel too** |
| `ADMIN_URL` | `afronative-admin-panel` |
| `CSRF_TRUSTED_ORIGINS` | `https://afronative-admin.onrender.com` |

### 3.3 Deploy

Click **Create Web Service**. Render will build and deploy — it takes 5–10 minutes.

After deployment, Render gives you a URL like:

```
https://afronative-admin.onrender.com
```

**Save this URL** — you'll need it for Vercel.

### 3.4 Create the Superuser (Admin Account)

1. Go to your Django service on Render dashboard
2. Click **Shell** tab
3. Run: `python manage.py createsuperuser`
4. Enter username, email, and password

Your admin will be at:
```
https://afronative-admin.onrender.com/afronative-admin-panel/
```

---

## Step 4: Prepare the Express Website for Vercel

### 4.1 Create `vercel.json`

Create a file called `vercel.json` in `C:\Users\SHARP\Desktop\Afro_Naitive\`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "server.js",
      "use": "@vercel/node"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "server.js"
    }
  ]
}
```

This tells Vercel to run `server.js` as a Node.js server and route all requests to it.

### 4.2 Commit and Push

```powershell
cd C:\Users\SHARP\Desktop\Afro_Naitive
git add vercel.json
git commit -m "Add Vercel config for deployment"
git push
```

---

## Step 5: Deploy Express on Vercel

### 5.1 Import Project

1. Go to [vercel.com](https://vercel.com) and sign up (free with GitHub)
2. Click **Add New...** → **Project**
3. Click **Import Git Repository** and select your Express repo (`afronative-website`)
4. Vercel will auto-detect it as Node.js
5. Click **Deploy**

### 5.2 Set Environment Variables

1. Go to your project on the [Vercel dashboard](https://vercel.com/dashboard)
2. Click **Settings** → **Environment Variables**
3. Add these (select **Production** environment):

| Name | Value |
|------|-------|
| `NODE_ENV` | `production` |
| `DJANGO_API_URL` | `https://afronative-admin.onrender.com` (your Django URL from Step 3.3) |
| `SITE_API_KEY` | Same key you generated in Step 3.2 — **must match exactly** |

### 5.3 Redeploy

After setting env vars, trigger a redeploy from the Vercel dashboard (Deployments → Redeploy).

Your public website URL will be:
```
https://afronative-website.vercel.app
```

---

## Step 6: End-to-End Testing

### 6.1 Test the Django API

Open your browser:
```
https://afronative-admin.onrender.com/api/v1/site-content/
```
You should see `{"error": "Unauthorized"}` — this is correct! The API is protected.

### 6.2 Test the Website

1. Open: `https://afronative-website.vercel.app`
2. The site should load with data from Django
3. Open browser console (F12) — no errors

### 6.3 Test the Live Connection

1. Log in to the Django admin on Render
2. Add a new event with a future date, upload a flyer, check "Published", save
3. Wait up to 60 seconds (cache expiry)
4. Refresh the Vercel website
5. Your new event should appear! 🎉

---

## Architecture Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Django Admin   │────────>│   JSON API       │────────>│  Express Website│
│  (Render)       │         │  (X-API-Key auth)│         │  (Vercel)       │
│  • Events       │    JSON │ • Published only │   Merge │ • EJS templates │
│  • Hero Slides  │────────>│ • Future events  │────────>│ • 60-sec cache  │
│  • Cloudinary   │         │ • Past events    │         │ • Static fallback│
└─────────────────┘         └──────────────────┘         └─────────────────┘
        │                                                          │
        ▼                                                          ▼
┌─────────────────┐                              ┌──────────────────┐
│   Cloudinary    │                              │     Neon Postgres│
│   (Images)      │                              │   (Database)     │
└─────────────────┘                              └──────────────────┘
```

---

## Free Tier Summary

| Service | What You Get |
|---------|-------------|
| **Render** (Django) | 750 hrs/month, 1 GB bandwidth, sleeps after 15 min inactivity |
| **Vercel** (Express) | 100 GB bandwidth, **no sleep**, global CDN, free HTTPS |
| **Neon** (Database) | 500 MB storage, 10 connections |
| **Cloudinary** (Images) | 25 GB storage, 25 GB bandwidth |

For a small events website, these limits are more than enough.

---

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| Django won't start on Render | Check Render logs — usually a missing env var or wrong `DATABASE_URL` |
| 502 Bad Gateway on Render | Service is sleeping — wait 30 seconds and refresh |
| Express on Vercel can't reach Django | Check `DJANGO_API_URL` and `SITE_API_KEY` match on both sides |
| Vercel shows "Build Failed" | Check Vercel build logs — usually a missing dependency |
| Vercel returns 404 for all routes | Make sure `vercel.json` exists and is correct |
| Admin login doesn't work | Create superuser via Render shell (Step 3.4) |
| Static files 404 on Django | Run `python manage.py collectstatic` in Render shell |

---

## Quick Checklist

1. ⬜ Create `requirements.txt` and `Procfile` in Django project
2. ⬜ Push Django to GitHub
3. ⬜ Create Neon Postgres database
4. ⬜ Deploy Django on Render with all env vars
5. ⬜ Create superuser via Render Shell
6. ⬜ Create `vercel.json` in Express project
7. ⬜ Push to GitHub
8. ⬜ Deploy Express on Vercel with env vars
9. ⬜ Test the full chain end-to-end
10. ⬜ Share the Vercel URL with your client!
