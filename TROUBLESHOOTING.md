# 📋 Troubleshooting Log — AfroNative Admin Panel

> **Purpose:** This document records every problem we encountered while building the AfroNative admin panel and how each one was resolved. It serves as a reference for future debugging and learning.
> **Date:** November 16, 2026
> **Author:** Code_crush (with Junie assistance)

---

## Table of Contents

1. [Environment Setup Issues](#1-environment-setup-issues)
2. [Django Admin Styling Issues](#2-django-admin-styling-issues)
3. [Cloudinary Image Upload Issues](#3-cloudinary-image-upload-issues)
4. [API Image URL Issues](#4-api-image-url-issues)
5. [Express Website Issues](#5-express-website-issues)
6. [Data Merging and Fallback Issues](#6-data-merging-and-fallback-issues)
7. [Server Management Issues](#7-server-management-issues)

---

## 1. Environment Setup Issues

### 1.1 pip Can't Download Packages — DNS Resolution Failed

**Problem:**
When trying to install Django and other packages, pip failed with:
```
Could not resolve host: files.pythonhosted.org
```

**Root Cause:**
The network had intermittent DNS resolution issues. Pinging `files.pythonhosted.org` showed 75% packet loss, meaning the connection to the Python package server was unstable.

**Solution:**
Used two strategies:
1. **`--timeout=300`** — Gave pip 300 seconds (instead of the default 15) to download packages.
2. **`--trusted-host`** — Told pip to trust the package servers even if SSL verification had issues.

```powershell
.\venv\Scripts\Activate.ps1
pip install django cloudinary python-dotenv --timeout=300 --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

**Lesson Learned:**
Network issues can block package installation. Increasing the timeout and trusting hosts can help on unstable connections.

---

### 1.2 Virtual Environment Activation Failed

**Problem:**
Running `.\venv\Scripts\Activate.ps1` failed with:
```
Activate.ps1 cannot be loaded because running scripts is disabled on this system
```

**Root Cause:**
PowerShell's default execution policy on Windows blocks script execution for security reasons.

**Solution:**
Run this command once to allow scripts in the current user's scope:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Lesson Learned:**
Windows PowerShell has strict security policies by default. You may need to adjust them for development work.

---

## 2. Django Admin Styling Issues

### 2.1 Admin Panel Has No CSS — Unstyled and Broken Layout

**Problem:**
The Django admin panel at `http://127.0.0.1:8000/afronative-admin/` displayed with no CSS styling — plain text, no colors, no layout structure.

**Root Cause:**
Two issues combined:
1. **Missing `STATIC_ROOT` setting** — Django didn't know where to collect static files (CSS, JavaScript).
2. **`DEBUG=False` in `.env`** — This prevented the development server from serving static files automatically.

**Solution:**

**Step 1:** Added `STATIC_ROOT` to `afronative/settings.py`:
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

**Step 2:** Collected static files:
```powershell
python manage.py collectstatic
```
This gathered 130 CSS and JavaScript files into the `staticfiles` folder.

**Step 3:** Added static file serving to `afronative/urls.py`:
```python
from django.conf import settings
from django.conf.urls.static import static

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
```

**Step 4:** Changed `DEBUG=True` in `.env` for local development.

**Lesson Learned:**
- Always use `DEBUG=True` for local development. It enables static file serving and detailed error messages.
- When deploying to production, change back to `DEBUG=False` and use WhiteNoise or a proper web server (Nginx) to serve static files.
- `STATIC_ROOT` tells Django where to store collected static files.

---

## 3. Cloudinary Image Upload Issues

### 3.1 Wrong Cloud Name — Images Saved Locally Instead of Cloudinary

**Problem:**
When uploading images through the Django admin, images were saved to local folders (`event_flyers/`, `hero_slides/`) instead of uploading to Cloudinary. The API returned relative paths like `/event_flyers/photo.jpg` instead of Cloudinary HTTPS URLs.

**Root Cause:**
The user provided the Cloudinary **account name** (`Afro_native`) instead of the **cloud name** (`ivdqe3xb`). The Cloudinary SDK rejected the wrong cloud name with "Invalid cloud_name" error, so images fell back to local storage.

**How to Find the Correct Cloud Name:**
1. Log in to https://cloudinary.com/console
2. Look at the top of the dashboard — you'll see "Cloud name" with a value
3. It's usually a short code like `dexample123` or `ivdqe3xb`

**Solution:**
Updated the `.env` file with the correct cloud name:
```
# Wrong:
CLOUDINARY_URL=cloudinary://791596688669264:N0TFwZlX62TW35nCOD8jn9Qh3LI@Afro_native

# Correct:
CLOUDINARY_URL=cloudinary://791596688669264:N0TFwZlX62TW35nCOD8jn9Qh3LI@ivdqe3xb
```

**Lesson Learned:**
- **Account name** = Your brand name (for display)
- **Cloud name** = Your unique server ID (for API calls)
- Always use the **cloud name** in your code, not the account name!

---

### 3.2 Cloudinary SDK Not Configured — No Image Uploads

**Problem:**
Even with the correct `CLOUDINARY_URL` in `.env`, the Cloudinary Python SDK wasn't actually configured. The `django-cloudinary-storage` package read the URL but didn't pass it to the SDK.

**Root Cause:**
The `CLOUDINARY_URL` environment variable was set, but `cloudinary.config()` was never called with the parsed credentials.

**Solution:**
Added manual configuration in `afronative/settings.py`:
```python
import cloudinary
from urllib.parse import urlparse

parsed = urlparse(CLOUDINARY_URL)
cloud_name = parsed.hostname
api_key = parsed.username
api_secret = parsed.password

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=api_secret,
    secure=True,  # Force HTTPS URLs
)
```

**Lesson Learned:**
Setting environment variables isn't enough — you must also parse them and pass them to the SDK. Some packages do this automatically, but Cloudinary requires manual configuration.

---

### 3.3 Case-Sensitive Cloud Name — `urlparse` Lowercased the Hostname

**Problem:**
After configuring Cloudinary, uploads still failed. The cloud name was being lowercased by Python's `urlparse()` function.

**Root Cause:**
Python's `urlparse()` lowercases the hostname by default. Cloudinary cloud names are **case-sensitive**, so `ivdqe3xb` became `ivdqe3xb` (which happened to work in this case, but could have failed with mixed-case names).

**Solution:**
Extracted the cloud name directly from the raw URL string instead of using `urlparse()`:
```python
# Extract cloud name with original case from the raw URL string
if '@' in CLOUDINARY_URL:
    cloud_name = CLOUDINARY_URL.split('@')[-1]
else:
    cloud_name = parsed.hostname
```

**Lesson Learned:**
Be careful with URL parsing functions — they may modify the data in unexpected ways. Always verify the output matches the expected format.

---

### 3.4 Missing Images on Cloudinary — 404 Not Found

**Problem:**
Some images that were uploaded before the Cloudinary fix were missing from Cloudinary. Testing the URLs returned `404 Not Found`.

**Root Cause:**
Images uploaded before Cloudinary was properly configured were saved to local folders. When the API tried to construct Cloudinary URLs for these local paths, the URLs pointed to non-existent files on Cloudinary.

**Solution:**
Created a migration script (`reupload_images.py`) that:
1. Found images in local folders
2. Re-uploaded them to Cloudinary using the SDK
3. Updated the database records with the new Cloudinary public IDs

```python
from cloudinary.uploader import upload

result = upload(
    local_path,
    folder='event_flyers',
    public_id='IMG_4220',
    overwrite=True,
    resource_type='image',
)
```

**Lesson Learned:**
When fixing a storage backend, you must also migrate existing data. New uploads will work, but old records still point to the old storage location.

---

## 4. API Image URL Issues

### 4.1 API Returns Relative Paths Instead of HTTPS URLs

**Problem:**
The Django API returned relative paths like `/event_flyers/photo.jpg` instead of full Cloudinary HTTPS URLs. The Express site couldn't load these images because they were relative to the Express server, not the Django server.

**Root Cause:**
The API used `event.flyer.url` which returns a relative path for local files. For Cloudinary files, it should return the full HTTPS URL.

**Solution:**
Created a helper function `to_absolute_image_url()` in `events/api.py`:
```python
def to_absolute_image_url(image_field):
    if not image_field:
        return ""
    
    url = image_field.url
    
    # If already an absolute URL, return as-is
    if url.startswith('http://') or url.startswith('https://'):
        if url.startswith('http://'):
            url = 'https://' + url[7:]
        return url
    
    # It's a relative path — construct a Cloudinary URL
    cloud_name = get_cloud_name()
    if not cloud_name:
        return url
    
    public_id = url.lstrip('/')
    cloudinary_url = f'https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}'
    return cloudinary_url
```

Applied this function to all image fields in the API:
- Event flyers
- Past event gallery photos
- Hero slide images

**Lesson Learned:**
Always return absolute URLs in APIs. Relative paths only work when the client and server are on the same domain, which isn't the case here (Django on Render, Express on Vercel).

---

### 4.2 Cloudinary Config Not Available in API Function

**Problem:**
The `to_absolute_image_url()` function called `cloudinary.config().cloud_name`, but the config was sometimes not available or had the wrong cloud name.

**Root Cause:**
The `cloudinary.config()` object was set up in `settings.py`, but by the time the API function ran, the config might have been reset or had the wrong case.

**Solution:**
Created a separate function `get_cloud_name()` that extracts the cloud name directly from `settings.CLOUDINARY_URL`:
```python
def get_cloud_name():
    cloudinary_url = getattr(settings, 'CLOUDINARY_URL', '')
    if not cloudinary_url or '@' not in cloudinary_url:
        return None
    return cloudinary_url.split('@')[-1]
```

This bypasses the `cloudinary.config()` object entirely and reads the cloud name directly from the settings.

**Lesson Learned:**
Don't rely on global state (like `cloudinary.config()`) in API functions. Read directly from settings or environment variables for reliability.

---

## 5. Express Website Issues

### 5.1 Missing Flyer Image in EJS Template

**Problem:**
The event flyer image didn't appear on the Express website. Only the text (name, tagline, specs) was visible.

**Root Cause:**
The `upcoming-event.ejs` template had CSS styles for `.flyer-img-wrap` but never rendered the `<img>` tag for `upcomingEvent.flyer`. The template was designed for static data and didn't include the flyer image element.

**Solution:**
Added the flyer image wrapper to `upcoming-event.ejs`:
```html
<%# Flyer image — only show if a flyer URL exists %>
<% if (upcomingEvent.flyer) { %>
<div class="flyer-img-wrap">
  <img src="<%= upcomingEvent.flyer %>" alt="<%= upcomingEvent.flyerAlt || upcomingEvent.name %>" loading="lazy">
</div>
<% } %>
```

**Lesson Learned:**
When integrating a new data source (Django API), always check that all template elements are present to display the new data. CSS styles alone don't render content — you need the HTML elements too.

---

### 5.2 Express Server Not Running

**Problem:**
The Express website at `http://localhost:3000` was not accessible, even though the Django admin was running fine.

**Root Cause:**
The Express server had stopped (either crashed or was manually stopped). The user only had the Django server running.

**Solution:**
Started the Express server in a separate terminal:
```powershell
cd C:\Users\SHARP\Desktop\Afro_Naitive
node server.js
```

**Lesson Learned:**
Two servers, two roles:
- **Django** (Admin + API) — Port 8000 — Stores data and serves the API
- **Express** (Public Website) — Port 3000 — Renders the public-facing site

Both must be running for the full system to work. Think of Django as the kitchen (prepares data) and Express as the restaurant (serves data to customers). If the restaurant closes, customers can't eat, even if the kitchen is cooking!

---

## 6. Data Merging and Fallback Issues

### 6.1 Empty Django Hero Slides Overwrote Static Hero Slides

**Problem:**
When the Django API returned an empty `heroSlides: []` array, it overwrote the original static hero slides from `site.js`, causing the hero section to disappear.

**Root Cause:**
The merge logic in `content.js` blindly replaced the static data with whatever Django returned, even if it was empty:
```javascript
// OLD: Replace even if empty
if (djangoData.heroSlides && Array.isArray(djangoData.heroSlides)) {
    merged.assets.heroSlides = djangoData.heroSlides;
}
```

**Solution:**
Added a length check to only replace when Django has actual data:
```javascript
// NEW: Only replace if Django has actual slides
if (djangoData.heroSlides && 
    Array.isArray(djangoData.heroSlides) && 
    djangoData.heroSlides.length > 0) {
    merged.assets.heroSlides = djangoData.heroSlides;
}
```

**Lesson Learned:**
Never blindly overwrite data with potentially empty results. Always check if the new data is actually meaningful before replacing the old data. This is called **"smart merge with fallback"**.

---

### 6.2 Django Hero Slides Not Appearing on Express Site

**Problem:**
After adding hero slides in the Django admin and checking "Active", they still didn't appear on the Express website.

**Root Cause:**
The images were uploaded to Cloudinary, but the API was returning relative paths instead of HTTPS URLs (see Section 4.1). The Express site couldn't load relative paths from a different server.

**Solution:**
Fixed the `to_absolute_image_url()` function in the API (see Section 4.1) to return proper Cloudinary HTTPS URLs for all image types, including hero slides.

**Lesson Learned:**
When debugging cross-server image issues, always check the actual URLs being returned by the API. Use browser developer tools or console logs to inspect the data.

---

## 7. Server Management Issues

### 7.1 Multiple Python Processes Running in Background

**Problem:**
After making changes to `settings.py`, the changes weren't taking effect. The API kept returning old data.

**Root Cause:**
Multiple old Python processes were running in the background with cached code. The Django development server wasn't the only process — previous instances were still alive.

**Solution:**
Killed all old Python processes and restarted the Django server:
```powershell
Get-Process python | Where-Object { $_.Path -like "*Afronative*" } | Stop-Process -Force
python manage.py runserver
```

**Lesson Learned:**
Always check for and kill old server processes before restarting. Cached code in old processes can cause confusing behavior where changes don't seem to take effect.

---

### 7.2 Cache Delay — New Data Takes 60 Seconds to Appear

**Problem:**
After adding an event in the Django admin, it took up to 60 seconds to appear on the Express website.

**Root Cause:**
The `content.js` module implements a 60-second cache. This is intentional for performance — Django doesn't get hammered on every page load.

**Solution:**
This is by design, not a bug. To see changes immediately during development, you can:
1. Wait 60 seconds for the cache to expire
2. Restart the Express server to clear the cache
3. Temporarily reduce the cache duration in `content.js` (not recommended for production)

**Lesson Learned:**
Caching is a trade-off between freshness and performance. 60 seconds is a good balance for event data that doesn't change constantly. This is called **eventual consistency** — the data eventually becomes consistent, but there's a short delay.

---

## Summary of Key Lessons

| Lesson | Why It Matters |
|--------|---------------|
| **Use cloud name, not account name** | Cloudinary API calls fail with the wrong identifier |
| **Always return absolute URLs in APIs** | Relative paths don't work across different servers |
| **Check for empty data before merging** | Empty arrays can wipe out valid fallback data |
| **Both servers must run** | Django and Express are separate processes |
| **Kill old processes before restarting** | Cached code in old processes causes confusion |
| **`DEBUG=True` for local, `False` for production** | Development features vs. security |
| **Migrate existing data when changing storage** | New uploads work, but old records need updating |
| **Parse URLs carefully** | Functions like `urlparse()` can modify data unexpectedly |

---

## How to Use This Document

1. **When you encounter a problem**, search this document for keywords related to your issue.
2. **Read the "Root Cause" section** to understand why the problem happened.
3. **Follow the "Solution" section** to fix it.
4. **Review the "Lesson Learned"** to prevent it from happening again.

If you encounter a new problem not covered here, add it to this document with the same format: Problem → Root Cause → Solution → Lesson Learned.

---

*Document created on November 16, 2026. Last updated: November 16, 2026.*
