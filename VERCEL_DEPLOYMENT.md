# 🚀 Hybrid Deployment: Django on Render + Express on Vercel

## Overview

You'll deploy your two apps on different platforms:

1. **Django Admin** → **Render** (free tier) — Best for Python/Django apps
2. **Express Website** → **Vercel** (free tier) — Best for Node.js/JavaScript apps

Both apps will communicate via the JSON API, protected by a secret `SITE_API_KEY`.

### Why This Combination?

| Platform | Best For | Why? |
|----------|----------|------|
| **Render** | Django | Supports always-on servers, easy Postgres setup, built-in shell for superuser |
| **Vercel** | Express | Instant deployments, free HTTPS, global CDN, automatic preview URLs |

---

## Prerequisites

- A **Render account** at [render.com](https://render.com) (free with GitHub)
- A **Vercel account** at [vercel.com](https://vercel.com) (free with GitHub)
- A **Cloudinary account** at [cloudinary.com](https://cloudinary.com) (free tier)
- A **Neon account** at [neon.tech](https://neon.tech) for Postgres (free tier)
- Your Django project pushed to a **GitHub repository**
- Your Express project pushed to a **GitHub repository**

---

## Step 1: Deploy Django on Render

### 1.1 Prepare Your Django Project

Ensure you have these files:

**`requirements.txt`** (create if missing):
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

**`Procfile`** (create if missing):
```
web: gunicorn afronative.wsgi:application --bind 0.0.0.0:$PORT
```

**`.gitignore`** (should already exist):
```
.env
db.sqlite3
__pycache__/
*.pyc
venv/
*.egg-info/
instance/
```

### 1.2 Push Django to GitHub

```powershell
cd C:\Users\SHARP\Desktop\Afronative_admin_sites
git init
git add .
git commit -m "Initial commit: Django admin for AfroNative"
# Create a repo on GitHub, then:
git remote add origin https://github.com/your-username/afronative-admin.git
git push -u origin main
```

### 1.3 Set Up Postgres Database (Neon)

1. Go to [neon.tech](https://neon.tech) and sign up (free)
2. Create a new project called `afronative-admin`
3. Neon will give you a **connection string** like:
```
postgresql://user:password@ep-cool-dynamic-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
```
4. Copy this connection string — you'll need it soon

### 1.4 Create a Web Service on Render

1. Go to your [Render dashboard](https://dashboard.render.com/)
2. Click **New +** → **Web Service**
3. Connect your GitHub repo (the Django admin repo)
4. Fill in the details:

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

### 1.5 Set Environment Variables

In the **Environment Variables** section, add these:

| Name | Value |
|------|-------|
| `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `afronative-admin.onrender.com` |
| `DATABASE_URL` | Paste your Neon connection string |
| `CLOUDINARY_URL` | `cloudinary://791596688669264:N0TFwZlX62TW35nCOD8jn9Qh3LI@Afro_native` |
| `SITE_API_KEY` | Generate a random key (see Step 2) |
| `ADMIN_URL` | `afronative-admin-panel` |
| `CSRF_TRUSTED_ORIGINS` | `https://afronative-admin.onrender.com` |

### 1.6 Deploy and Note Your URL

Click **Create Web Service**. After deployment, Render will give you a URL like:

```
https://afronative-admin.onrender.com
```

**Save this URL** — you'll need it for Vercel.

### 1.7 Create the Superuser

1. Go to your Django service on Render dashboard
2. Click **Shell** tab
3. Run: `python manage.py createsuperuser`
4. Enter username: `Code_crush`, email (optional), and your password

Your admin will be at:
```
https://afronative-admin.onrender.com/afronative-admin-panel/
```

---

## Step 2: Generate the Shared API Key

### 2.1 Generate a Random Key

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

This produces something like: `vX9zK2mP4qR7sT1wY3aB5cD6eF8gH0jL`

### 2.2 Set It on Both Sides

- **Django on Render**: Already set as `SITE_API_KEY` in Step 1.5
- **Express on Vercel**: You'll set it in Step 3.4

**Both must match exactly.**

---

## Step 3: Deploy Express on Vercel

### 3.1 Prepare Your Express Project

Vercel needs a config file to know how to run your Express app. Create `vercel.json` in your Express project root (`C:\Users\SHARP\Desktop\Afro_Naitive\`):

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

**📚 What this file does (Learning Moment):**
Vercel is designed for static sites and serverless functions by default. The `vercel.json` file tells Vercel: "Hey, this is a Node.js server app, not just static files. Run `server.js` as the entry point and send all requests to it." Without this file, Vercel wouldn't know how to handle your Express server.

### 3.2 Push Express to GitHub

```powershell
cd C:\Users\SHARP\Desktop\Afro_Naitive
git init
git add .
git commit -m "Initial commit: AfroNative Express website with Vercel config"
# Create a repo on GitHub, then:
git remote add origin https://github.com/your-username/afronative-website.git
git push -u origin main
```

### 3.3 Import Project on Vercel

1. Go to [vercel.com](https://vercel.com) and sign up (free with GitHub)
2. Click **Add New...** → **Project**
3. Click **Import Git Repository** and select your Express repo (`afronative-website`)
4. Vercel will auto-detect it as a Node.js project
5. Click **Deploy**

Vercel will build and deploy your app automatically. It usually takes 1-2 minutes.

### 3.4 Set Environment Variables

1. Go to your project on the [Vercel dashboard](https://vercel.com/dashboard)
2. Click **Settings** → **Environment Variables**
3. Add these variables:

| Name | Value | Environment |
|------|-------|-------------|
| `NODE_ENV` | `production` | Production |
| `DJANGO_API_URL` | `https://afronative-admin.onrender.com` (your Django URL from Step 1.6) | Production |
| `SITE_API_KEY` | Same key you generated in Step 2 | Production |

**Important:** Make sure you select **Production** environment (not Development or Preview).

**📚 What environment variables do on Vercel:**
When your Express code does `process.env.DJANGO_API_URL`, Vercel replaces it with the value you set here. This way, you never hardcode URLs or secrets in your code. Each environment (Production, Development, Preview) can have different values.

### 3.5 Note Your Vercel URL

After deployment, Vercel will give you a URL like:

```
https://afronative-website.vercel.app
```

This is your **public website URL** — share it with your client!

**📚 Bonus:** Vercel lets you set a custom domain (like `afronative.com`) for free. Go to **Settings** → **Domains** to add yours.

---

## Step 4: End-to-End Testing

### 4.1 Test the Django API

Open your browser:
```
https://afronative-admin.onrender.com/api/v1/site-content/
```

You should see: `{"error": "Unauthorized"}` — this is correct! The API is protected.

To test properly, use **curl** or **Postman**:
```powershell
curl -H "X-API-Key: your-secret-key" https://afronative-admin.onrender.com/api/v1/site-content/
```

You should see JSON with `upcomingEvents`, `pastEvent`, and `heroSlides`.

### 4.2 Test the Express Website on Vercel

1. Open: `https://afronative-website.vercel.app`
2. The site should load with data from Django
3. Open browser console (F12) — you should see no errors

### 4.3 Test the Live Connection

1. Log in to the Django admin on Render
2. Add a new event with a future date
3. Upload a flyer image (it should go to Cloudinary)
4. Check "Published"
5. Save
6. Wait up to 60 seconds (cache expiry)
7. Refresh the Vercel website
8. Your new event should appear! 🎉

### 4.4 Test the Fallback

1. Pause the Django service on Render (dashboard → Pause)
2. Wait a minute
3. Refresh the Vercel website
4. It should still work, showing the last cached data or static fallback
5. Resume the Django service on Render
6. Wait 60 seconds
7. Refresh — live data should come back

---

## Step 5: How Vercel Deployments Work (Learning Moment 📚)

### Automatic Deployments on Vercel

Vercel has a superpower: **every time you push to GitHub, Vercel automatically redeploys your site.**

Here's the flow:
```
You push code to GitHub
        ↓
Vercel detects the new commit
        ↓
Vercel builds the project (runs npm install)
        ↓
Vercel deploys the new version
        ↓
Your site is updated (usually within 1-2 minutes)
```

**No manual clicks needed.** This is called **Continuous Deployment (CD)** — a professional practice where code changes go live automatically.

### Preview Deployments

If you create a Git branch (e.g., `feature/new-design`), Vercel creates a **preview URL** for that branch. This lets you test changes before merging to `main`.

Example:
- `https://afronative-website-git-feature-new-design.vercel.app` → Preview
- `https://afronative-website.vercel.app` → Production (main branch)

### Why Vercel is Great for Express

| Feature | Benefit |
|---------|---------|
| **Global Edge Network** | Your site loads fast from anywhere in the world |
| **Free HTTPS** | Automatic SSL certificates, no setup needed |
| **Instant Rollbacks** | Click one button to revert to a previous version |
| **Zero Config** | Vercel detects Node.js projects automatically |
| **Free Custom Domains** | Connect your own domain name for free |

---

## Step 6: How to Rotate the API Key

If you suspect the key is compromised:

### 6.1 Generate a New Key

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6.2 Update Both Services

1. **Django on Render**: Go to Render dashboard → Django service → Environment Variables → Edit `SITE_API_KEY` → Save (auto-deploys)
2. **Express on Vercel**: Go to Vercel dashboard → Project → Settings → Environment Variables → Edit `SITE_API_KEY` → Redeploy

### 6.3 Test

After both services update, test the API endpoint and the Vercel website to confirm they still communicate.

---

## Free Tier Limits

### Render Free Tier (Django)

| Resource | Limit |
|----------|-------|
| Web Services | 750 hours/month (enough for 1 app always on) |
| Bandwidth | 1 GB/month |
| Sleep | Free services sleep after 15 min of inactivity |

**Note:** When Django sleeps, the first request after waking takes ~30 seconds. This is normal on the free tier.

### Vercel Free Tier (Express)

| Resource | Limit |
|----------|-------|
| Bandwidth | 100 GB/month |
| Executions | Unlimited |
| Build Minutes | 6,000 minutes/month |
| Sleep | **No sleep** — your site is always on |

**Vercel's free tier is very generous** for a website like yours.

### Neon Free Tier (Postgres)

| Resource | Limit |
|----------|-------|
| Database Size | 500 MB |
| Concurrent Connections | 10 |

### Cloudinary Free Tier (Images)

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
| 502 Bad Gateway on Render | Service is sleeping — wait 30 seconds and refresh |
| Cloudinary uploads fail | Verify `CLOUDINARY_URL` format: `cloudinary://KEY:SECRET@CLOUD_NAME` |
| Express on Vercel can't reach Django | Check `DJANGO_API_URL` and `SITE_API_KEY` match on both sides |
| Vercel shows "Build Failed" | Check Vercel build logs — usually a missing dependency in `package.json` |
| Vercel returns 404 for all routes | Make sure `vercel.json` exists and routes are configured correctly |
| Admin login doesn't work | Create superuser via Render shell (Step 1.7) |
| Static files 404 on Django | Run `python manage.py collectstatic` in Render shell |

---

## 📚 Summary — Your Architecture

### How Everything Connects

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Django Admin   │────────>│   JSON API       │────────>│  Express Website│
│  (Render)       │         │  (X-API-Key auth)│         │  (Vercel)       │
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

1. **You** log in to Django admin on Render → add/edit events → images go to Cloudinary
2. **Django API** exposes published events as JSON (protected by API key)
3. **Express on Vercel** fetches JSON every 60 seconds → merges with static data → renders EJS
4. **Visitors** see the live website with your latest events

### Security Checklist

- ✅ Admin panel protected by Django authentication
- ✅ API protected by secret key (`X-API-Key` header)
- ✅ Credentials in environment variables (never committed to GitHub)
- ✅ Secure cookies and HTTPS in production
- ✅ Timing-safe key comparison (`hmac.compare_digest`)

---

## 🎯 Your Next Steps

1. **Push Django to GitHub** → Deploy on Render
2. **Create Neon Postgres database** → Connect to Django
3. **Create superuser via Render shell**
4. **Add `vercel.json` to Express project**
5. **Push Express to GitHub** → Deploy on Vercel
6. **Set environment variables on Vercel**
7. **Test the whole chain**
8. **Share the Vercel URL with your client!**

---

## 💡 Learning Question

**Why does Vercel not "sleep" like Render's free tier?**

Vercel uses a **serverless architecture** — your code runs in short-lived containers that spin up only when needed. Since there's no always-on server to keep alive, there's no "sleep" concept. Render's free tier, on the other hand, gives you a real server that sleeps after inactivity to save resources. Both approaches work, but Vercel's model is better for public websites that need to be always responsive.

---

**🎉 Congratulations! With Django on Render and Express on Vercel, you're using the best tool for each job — a professional approach!**
