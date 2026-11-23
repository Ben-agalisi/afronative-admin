# 🚀 Phase 4 — Deployment Guide

## Overview

You'll deploy two separate apps on **Render** (free tier):

1. **Django Admin** — Backend with Postgres database and Cloudinary images
2. **Express Website** — Public-facing site that fetches from Django API

Both apps will share the same secret `SITE_API_KEY` for secure communication.

---

## Prerequisites

- A **Render account** at [render.com](https://render.com) (free with GitHub)
- A **Cloudinary account** at [cloudinary.com](https://cloudinary.com) (free tier)
- A **Neon account** at [neon.tech](https://neon.tech) for Postgres (free tier)
- Your Django project pushed to a **GitHub repository**
- Your Express project pushed to a **GitHub repository**

---

## Step 1: Prepare Your Django Project

### 1.1 Add Production Requirements

Create or update `requirements.txt` in your Django project root:

```
Django>=4.2
cloudinary
django-cloudinary-storage
python-dotenv
dj-database-url
gunicorn
whitenoise
psycopg2-binary
```

### 1.2 Create `Procfile` (Render needs this)

Create a file called `Procfile` in your Django project root:

```
web: gunicorn afronative.wsgi:application --bind 0.0.0.0:$PORT
```

This tells Render how to start your Django app with Gunicorn (production server).

### 1.3 Update `settings.py` for Production

Ensure your `afronative/settings.py` has these production settings:

```python
import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# Security — read from env vars
SECRET_KEY = os.getenv('SECRET_KEY', '')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database — SQLite in dev, Postgres in production
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
        ssl_require=True if not DEBUG else False,
    )
}

# Static files with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = 'static/'

# Secure cookies in production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
```

### 1.4 Update `.gitignore`

Ensure your `.gitignore` excludes these files:

```
.env
db.sqlite3
__pycache__/
*.pyc
venv/
*.egg-info/
instance/
```

### 1.5 Push to GitHub

```powershell
cd C:\Users\SHARP\Desktop\Afronative_admin_sites
git init
git add .
git commit -m "Initial commit: Django admin for AfroNative"
# Create a repo on GitHub, then:
git remote add origin https://github.com/your-username/afronative-admin.git
git push -u origin main
```

---

## Step 2: Set Up Postgres Database (Neon)

### 2.1 Create a Neon Account

1. Go to [neon.tech](https://neon.tech) and sign up (free)
2. Create a new project called `afronative-admin`
3. Neon will give you a **connection string** like:

```
postgresql://user:password@ep-cool-dynamic-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 2.2 Copy the Connection String

You'll paste this into Render as `DATABASE_URL` env var.

---

## Step 3: Deploy Django on Render

### 3.1 Create a New Web Service

1. Go to your [Render dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repo (the Django admin repo)
4. Fill in the details:

| Field | Value |
|-------|-------|
| Name | `afronative-admin` |
| Region | Choose closest to you (e.g., Frankfurt) |
| Branch | `main` |
| Root Directory | Leave blank (project root) |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn afronative.wsgi:application --bind 0.0.0.0:$PORT` |
| Type | **Free** |

### 3.2 Set Environment Variables

In the **Environment Variables** section, add these:

| Name | Value |
|------|-------|
| `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `afronative-admin.onrender.com` |
| `DATABASE_URL` | Paste your Neon connection string |
| `CLOUDINARY_URL` | `cloudinary://API_KEY:API_SECRET@CLOUD_NAME` (from your Cloudinary dashboard) |
| `SITE_API_KEY` | Generate a random key (see Step 4) |
| `ADMIN_URL` | `afronative-admin-panel` (custom path, not `/admin/`) |
| `CSRF_TRUSTED_ORIGINS` | `https://afronative-admin.onrender.com` |

### 3.3 Deploy

Click **Create Web Service**. Render will build and deploy your Django app. It may take 5-10 minutes.

### 3.4 Note Your Django URL

After deployment, Render will give you a URL like:

```
https://afronative-admin.onrender.com
```

You'll need this for the Express app.

---

## Step 4: Generate & Share the API Key

### 4.1 Generate a Random Key

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

This produces something like: `vX9zK2mP4qR7sT1wY3aB5cD6eF8gH0jL`

### 4.2 Set It on Both Sides

- **Django**: Set as `SITE_API_KEY` in Render env vars (Step 3.2)
- **Express**: Set as `SITE_API_KEY` in Render env vars (Step 6.2)

**Both must match exactly.**

---

## Step 5: Create the Superuser (Admin Account)

Since your Django app is on Render, you can't run `python manage.py createsuperuser` locally. Instead:

### 5.1 Connect to Render Shell

1. Go to your Django service on Render dashboard
2. Click **Shell** tab
3. You'll get a live terminal inside your deployed app

### 5.2 Run the Command

```bash
python manage.py createsuperuser
```

Enter:
- Username: `Code_crush`
- Email: (optional)
- Password: (your strong password)
- Password confirmation: (repeat)

### 5.3 Access the Admin

Your admin URL will be:

```
https://afronative-admin.onrender.com/afronative-admin-panel/
```

(Note: the path comes from your `ADMIN_URL` env var)

---

## Step 6: Deploy Express on Render

### 6.1 Prepare Your Express Project

Ensure your Express project has:

- `package.json` with dependencies
- `.gitignore` that excludes `.env` and `node_modules`
- All files committed and pushed to GitHub

### 6.2 Push Express to GitHub

```powershell
cd C:\Users\SHARP\Desktop\Afro_Naitive
git init
git add .
git commit -m "Initial commit: AfroNative Express website"
# Create a repo on GitHub, then:
git remote add origin https://github.com/your-username/afronative-website.git
git push -u origin main
```

### 6.3 Create a New Web Service on Render

1. Go to your [Render dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repo (the Express website repo)
4. Fill in the details:

| Field | Value |
|-------|-------|
| Name | `afronative-website` |
| Region | Same as Django (Frankfurt) |
| Branch | `main` |
| Root Directory | Leave blank |
| Runtime | `Node` |
| Build Command | `npm install` |
| Start Command | `node server.js` |
| Type | **Free** |

### 6.4 Set Environment Variables

| Name | Value |
|------|-------|
| `NODE_ENV` | `production` |
| `DJANGO_API_URL` | `https://afronative-admin.onrender.com` (your Django URL) |
| `SITE_API_KEY` | Same key you set for Django (Step 4) |
| `PORT` | `3000` |

### 6.5 Deploy

Click **Create Web Service**. Render will build and deploy your Express app.

### 6.6 Note Your Express URL

After deployment, Render will give you a URL like:

```
https://afronative-website.onrender.com
```

This is your **public website URL** — share it with your client!

---

## Step 7: End-to-End Testing

### 7.1 Test the Django API

Open your browser:

```
https://afronative-admin.onrender.com/api/v1/site-content/
```

You should see: `{"error": "Unauthorized"}` (because you're not sending the API key — this is correct!)

To test properly, use **curl** or **Postman**:

```powershell
curl -H "X-API-Key: your-secret-key" https://afronative-admin.onrender.com/api/v1/site-content/
```

You should see JSON with `upcomingEvents`, `pastEvent`, and `heroSlides`.

### 7.2 Test the Express Website

1. Open: `https://afronative-website.onrender.com`
2. The site should load with data from Django
3. Check the browser console — you should see no errors

### 7.3 Test the Live Connection

1. Log in to the Django admin
2. Add a new event with a future date
3. Upload a flyer image (it should go to Cloudinary)
4. Check "Published"
5. Save
6. Wait up to 60 seconds (cache expiry)
7. Refresh the Express website
8. Your new event should appear! 🎉

### 7.4 Test the Fallback

1. Pause the Django service on Render (dashboard → Pause)
2. Wait a minute
3. Refresh the Express website
4. It should still work, showing the last cached data or static fallback
5. Resume the Django service
6. Wait 60 seconds
7. Refresh — live data should come back

---

## Step 8: How to Rotate the API Key

If you suspect the key is compromised:

### 8.1 Generate a New Key

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 8.2 Update Both Services

1. **Django**: Go to Render dashboard → Django service → Environment Variables → Edit `SITE_API_KEY` → Deploy
2. **Express**: Go to Render dashboard → Express service → Environment Variables → Edit `SITE_API_KEY` → Deploy

### 8.3 Test

After both services redeploy, test the API endpoint and the Express website to confirm they still communicate.

---

## Free Tier Limits (as of 2024)

### Render Free Tier

| Resource | Limit |
|----------|-------|
| Web Services | 750 hours/month (enough for 1-2 apps always on) |
| Bandwidth | 1 GB/month |
| Database | Not available on free tier (use Neon instead) |
| Sleep | Free services sleep after 15 min of inactivity |

**Note:** When a service sleeps, the first request after waking takes ~30 seconds. This is normal on the free tier.

### Neon Free Tier

| Resource | Limit |
|----------|-------|
| Database Size | 500 MB |
| Concurrent Connections | 10 |
| Branches | Unlimited |

### Cloudinary Free Tier

| Resource | Limit |
|----------|-------|
| Transformations | 25,000/month |
| Storage | 25 GB |
| Bandwidth | 25 GB/month |

For a small events website, these limits are more than enough.

---

## Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| Django app won't start on Render | Check Render logs — usually a missing env var or wrong `DATABASE_URL` |
| 502 Bad Gateway | Service is sleeping — wait 30 seconds and refresh |
| Cloudinary uploads fail | Verify `CLOUDINARY_URL` format: `cloudinary://KEY:SECRET@CLOUD_NAME` |
| Express can't reach Django | Check `DJANGO_API_URL` and `SITE_API_KEY` match on both sides |
| Static files 404 on Django | Run `python manage.py collectstatic` in Render shell |
| Admin login doesn't work | Create superuser via Render shell (Step 5) |

---

## 📚 Summary — What You've Built

### Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Django Admin   │────────>│   JSON API       │────────>│  Express Website│
│  (Render)       │         │  (X-API-Key auth)│         │  (Render)       │
│                 │         │                  │         │                 │
│ • Event model   │    JSON │ • Published only │   Merge │ • EJS templates │
│ • PastEvent     │────────>│ • Future events  │────────>│ • 60-sec cache  │
│ • HeroSlide     │         │ • Past events    │         │ • Static fallback│
│ • Cloudinary    │         │ • Ordered        │         │                 │
└─────────────────┘         └──────────────────┘         └─────────────────┘
        │                                              │
        ▼                                              ▼
┌─────────────────┐                              ┌──────────────────┐
│   Cloudinary    │                              │     Neon Postgres│
│   (Images)      │                              │   (Database)     │
└─────────────────┘                              └──────────────────┘
```

### Data Flow

1. **You** log in to Django admin → add/edit events → images go to Cloudinary
2. **Django API** exposes published events as JSON (protected by API key)
3. **Express** fetches JSON every 60 seconds → merges with static data → renders EJS
4. **Visitors** see the live website with your latest events

### Security

- ✅ Admin panel protected by Django authentication
- ✅ API protected by secret key (`X-API-Key` header)
- ✅ Credentials in `.env` files (never committed to GitHub)
- ✅ Secure cookies and HTTPS in production
- ✅ Timing-safe key comparison (`hmac.compare_digest`)

---

## 🎯 Your Next Steps

1. **Push both projects to GitHub**
2. **Create Neon Postgres database**
3. **Deploy Django on Render**
4. **Create superuser via Render shell**
5. **Deploy Express on Render**
6. **Test the whole chain**
7. **Share the Express URL with your client!**

---

## 💡 Learning Question

Now that you've seen the full architecture, think about this:

**What happens if your client adds an event in the Django admin at 10:00 AM, and a visitor loads the Express website at 10:01 AM?**

(Hint: Think about the 60-second cache and when it was last refreshed.)

---

**🎉 Congratulations! You've built a complete two-app system with Django admin, Cloudinary images, a secure API, and an Express website. This is real-world architecture used by professional developers!**
