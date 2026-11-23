# 📚 AfroNative Admin — Complete Beginner's Learning Guide

> **Welcome, Code_crush!** This guide explains everything we built, step by step, in simple terms. Read it at your own pace. Don't worry if some parts seem confusing at first — re-read them, and things will click.

---

## Table of Contents

1. [The Big Picture](#1-the-big-picture)
2. [Key Concepts You Need to Know](#2-key-concepts-you-need-to-know)
3. [Folder Structure](#3-folder-structure)
4. [Phase 1: Django Admin Setup](#4-phase-1-django-admin-setup)
5. [Phase 2: The JSON API](#5-phase-2-the-json-api)
6. [Phase 3: Express Website Connection](#6-phase-3-express-website-connection)
7. [Phase 4: Deployment](#7-phase-4-deployment)
8. [How to Run Everything Locally](#8-how-to-run-everything-locally)
9. [Common Questions](#9-common-questions)

---

## 1. The Big Picture

### What Did We Build?

We built **two separate applications** that talk to each other:

```
┌──────────────────────────┐
│   Django Admin Panel     │  ← You (the admin) log in here
│   (Private, password)    │    to add/edit events
│                          │
│   • Event data           │
│   • Image uploads        │
│   • Database storage     │
└──────────┬───────────────┘
           │
           │ Sends JSON data
           │ (protected by secret key)
           ▼
┌──────────────────────────┐
│   Express Website        │  ← Your visitors see this
│   (Public, no login)     │    It fetches data from Django
│                          │
│   • Shows events         │
│   • Renders HTML pages   │
│   • Caches data 60 sec   │
└──────────────────────────┘
```

### Why Two Apps?

Think of it like a restaurant:

- **Django Admin** = The kitchen (where you prepare the food/events)
- **Express Website** = The dining room (where customers see the menu)

The kitchen and dining room are separate, but they communicate through waiters (the API). This separation is good because:

1. **Security**: Only you can access the kitchen (admin login). Everyone can see the dining room (public website).
2. **Flexibility**: You can change the kitchen without affecting the dining room.
3. **Scalability**: If you get more customers, you can add more tables without changing the kitchen.

---

## 2. Key Concepts You Need to Know

### What is Django?

Django is a **Python web framework**. A framework is like a toolkit that gives you pre-built tools so you don't have to write everything from scratch.

**Analogy**: Building a house from scratch means making your own bricks, cement, and nails. Using Django is like going to a hardware store — the bricks and cement are already made, you just assemble them.

**What Django gives us for free:**
- A database system (to store events)
- An admin panel (to manage events)
- User authentication (login/password)
- URL routing (connecting URLs to pages)

### What is a Model?

A **model** is a Python class that defines a table in your database. Each model = one database table.

**Example**: Our `Event` model defines a table with columns like:
- `name` (text)
- `ends_at` (date/time)
- `flyer` (image)

Think of a model as a **form template** — it defines what information each event will have.

### What is an API?

**API** stands for Application Programming Interface. It's a way for two programs to talk to each other.

**Analogy**: When you order food at a restaurant, you don't go into the kitchen. You give your order to a waiter (the API), who takes it to the kitchen and brings back your food.

In our project:
- Express (the website) is the customer
- Django (the admin) is the kitchen
- The JSON API is the waiter

Express sends a request: "Give me the events" → Django responds with JSON data → Express displays it.

### What is JSON?

**JSON** (JavaScript Object Notation) is a format for sending data between programs. It looks like this:

```json
{
  "name": "Afro Music Festival",
  "date": "2026-12-01",
  "venue": "Lagos Convention Center"
}
```

It's like a universal language that both Python (Django) and JavaScript (Express) understand.

### What is Cloudinary?

**Cloudinary** is a cloud service for storing and serving images. Instead of storing images on your own server (which can fill up and slow down), you store them in the cloud.

**Analogy**: Instead of keeping all your photos in your phone's storage, you upload them to Google Photos. They're accessible from anywhere, and your phone doesn't fill up.

When you upload a flyer in the Django admin:
1. Django receives the image file
2. Django sends it to Cloudinary
3. Cloudinary gives back a URL (like `https://res.cloudinary.com/.../flyer.jpg`)
4. Django saves that URL in the database

### What is an Environment Variable?

An **environment variable** is a value that's stored outside your code, in the system environment. We use them for secrets like API keys and passwords.

**Why not put secrets in code?**
- If you share your code, you share your secrets
- If you push to GitHub, your secrets are public
- If someone hacks your code, they get your secrets

**Solution**: Store secrets in `.env` files (which are ignored by Git) or in environment variables on the server.

### What is `.env` and `.gitignore`?

- **`.env`** = A file that stores your secrets (API keys, passwords). It looks like this:
  ```
  SECRET_KEY=abc123xyz
  CLOUDINARY_URL=cloudinary://key:secret@cloud_name
  ```

- **`.gitignore`** = A file that tells Git which files to ignore when you push to GitHub. We add `.env` to it so your secrets are never uploaded.

**Analogy**: `.env` is your wallet (holds your money/secrets). `.gitignore` is the lock on your wallet (keeps it safe).

### What is a Virtual Environment?

A **virtual environment** (venv) is an isolated Python environment for your project. It keeps your project's dependencies separate from other projects.

**Analogy**: If you have multiple toolboxes at home, each room has its own. The kitchen toolbox has knives and spatulas, the garage has hammers and wrenches. A virtual environment is like a room-specific toolbox.

### What is a Database?

A **database** is organized storage for your data. Django uses SQLite by default (a simple file-based database) and can use PostgreSQL for production (a more powerful server-based database).

**Analogy**: A database is like a filing cabinet. Each table is a drawer, each row is a file, and each column is a field on the file.

### What is Migration?

A **migration** is how Django creates or changes database tables. When you create a model, you run `python manage.py migrate` to actually create the table in the database.

**Analogy**: A model is the blueprint of a house. A migration is the actual construction based on that blueprint.

---

## 3. Folder Structure

### Django Project (Afronative_admin_sites)

```
Afronative_admin_sites/
│
├── .env                    ← Your secrets (NEVER commit to GitHub)
├── .env.example            ← Template showing what env vars are needed
├── .gitignore              ← Tells Git which files to ignore
├── db.sqlite3              ← Your local database (NEVER commit)
├── manage.py               ← Django's command-line tool
├── DEPLOYMENT.md           ← Step-by-step deployment guide
├── LEARNING_GUIDE.md       ← This file!
│
├── afronative/             ← Django project settings
│   ├── settings.py         ← All configuration (database, security, Cloudinary)
│   ├── urls.py             ← Main URL routing (admin path, API path)
│   ├── wsgi.py             ← Production server configuration
│   └── asgi.py             ← Async server configuration
│
├── events/                 ← Your Django app (the main feature)
│   ├── models.py           ← Database models (Event, EventSpec, etc.)
│   ├── admin.py            ← Admin panel customization
│   ├── api.py              ← JSON API endpoint
│   ├── urls.py             ← API URL routing
│   ├── tests.py            ← Automated tests
│   └── views.py            ← (Optional) Custom page views
│
└── event_flyers/           ← Local image storage (fallback if no Cloudinary)
```

### Express Project (Afro_Naitive)

```
Afro_Naitive/
│
├── .env                    ← Django API URL and secret key
├── server.js               ← Main Express server file
│
├── src/
│   ├── data/
│   │   └── site.js         ← Static fallback content
│   ├── services/
│   │   └── content.js      ← Fetches data from Django API
│   └── views/              ← EJS HTML templates
│
└── public/                 ← CSS, JS, images
```

---

## 4. Phase 1: Django Admin Setup

### 4.1 The `.env` File

**Location**: `Afronative_admin_sites/.env`

This file stores all your secrets. Here's what each line does:

```env
SECRET_KEY=your-random-secret-key-here
```
- **What it is**: A long random string Django uses to encrypt cookies and passwords.
- **Why it matters**: Without this, Django can't secure your sessions. Never share it.

```env
DEBUG=False
```
- **What it is**: A switch that turns debug mode on/off.
- **Why it matters**: In development, `DEBUG=True` shows helpful error pages. In production, `DEBUG=False` hides sensitive info from attackers.

```env
ALLOWED_HOSTS=localhost,127.0.0.1
```
- **What it is**: A list of domains that can access your Django site.
- **Why it matters**: Prevents attackers from using your server with a fake hostname.

```env
DATABASE_URL=sqlite:///db.sqlite3
```
- **What it is**: The address of your database.
- **Why it matters**: Tells Django where to store and retrieve data. SQLite is a simple file-based database. In production, you'll use PostgreSQL.

```env
CLOUDINARY_URL=cloudinary://791596688669264:N0TFwZlX62TW35nCOD8jn9Qh3LI@Afro_native
```
- **What it is**: Your Cloudinary credentials in one string.
- **Why it matters**: This is how Django connects to Cloudinary to upload images. Format: `cloudinary://API_KEY:API_SECRET@CLOUD_NAME`

```env
SITE_API_KEY=afronative-secret-api-key-rotate-in-production-32bytes
```
- **What it is**: A secret key that Express uses to prove it's allowed to fetch data from Django.
- **Why it matters**: Without this, anyone could access your API. Both Django and Express must have the same key.

```env
ADMIN_URL=afronative-admin
```
- **What it is**: The URL path for your admin panel.
- **Why it matters**: Instead of the default `/admin/`, your admin is at `/afronative-admin/`. This is more secure because hackers usually try `/admin/` first.

```env
CSRF_TRUSTED_ORIGINS=http://localhost:8000
```
- **What it is**: A list of origins Django trusts for CSRF protection.
- **Why it matters**: CSRF (Cross-Site Request Forgery) is an attack where a malicious site tricks your browser into making requests on your site. This setting tells Django which origins are safe.

### 4.2 The `settings.py` File

**Location**: `Afronative_admin_sites/afronative/settings.py`

This is the brain of your Django project. Every configuration lives here.

**Key sections:**

```python
from dotenv import load_dotenv
load_dotenv()
```
- **What it does**: Loads all the variables from your `.env` file so you can use them in Python with `os.getenv()`.

```python
SECRET_KEY = os.getenv('SECRET_KEY', '')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
```
- **What it does**: Reads `SECRET_KEY` and `DEBUG` from the `.env` file. If `DEBUG` is missing, it defaults to `False` (safe).

```python
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
    )
}
```
- **What it does**: Configures the database. Uses `dj_database_url` to parse the `DATABASE_URL` env var. Falls back to SQLite if not set.

```python
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```
- **What it does**: Tells Django to use Cloudinary for all file uploads. When you upload an image in the admin, it goes straight to Cloudinary instead of your local disk.

```python
SITE_API_KEY = os.getenv('SITE_API_KEY', '')
```
- **What it does**: Stores the API key so the API view can check incoming requests.

### 4.3 The Models (`events/models.py`)

**Location**: `Afronative_admin_sites/events/models.py`

Models define your database structure. Let's break down each model:

#### Event Model

```python
class Event(models.Model):
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True)
    badge = models.CharField(max_length=100, default="Current Official Edition")
    ends_at = models.DateTimeField()
    flyer = models.ImageField(upload_to='event_flyers/')
    flyer_alt = models.CharField(max_length=200, blank=True)
    booking_text = models.TextField(blank=True)
    booking_label = models.CharField(max_length=100, blank=True)
    booking_url = models.URLField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**What each field means:**

| Field | Type | Purpose |
|-------|------|---------|
| `name` | CharField | The event's name (e.g., "PÁRTI EISAGÓSIS") |
| `tagline` | CharField | A short description (e.g., "TODAY WE PARTI • FIRST EDITION") |
| `badge` | CharField | A label shown on the event card (e.g., "Current Official Edition") |
| `ends_at` | DateTimeField | The date and time the event ends. Used to determine if it's upcoming or past. |
| `flyer` | ImageField | The event's promotional image. Uploaded to Cloudinary. |
| `flyer_alt` | CharField | Alternative text for the image (for accessibility and SEO) |
| `booking_text` | TextField | Description text for the booking button |
| `booking_label` | CharField | Text on the booking button (e.g., "Message on Instagram") |
| `booking_url` | URLField | The link the booking button points to |
| `is_published` | BooleanField | If `True`, the event appears on the website. If `False`, it's a draft. |
| `created_at` | DateTimeField | Automatically set when the event is first created |
| `updated_at` | DateTimeField | Automatically updated every time the event is edited |

**Why `is_published` exists**: It lets you create events in advance without them appearing on the website. You can prepare an event days before and publish it when you're ready.

#### EventSpec Model

```python
class EventSpec(models.Model):
    ICON_CHOICES = [
        ('calendar', 'Calendar'),
        ('clock', 'Clock'),
        ('pin', 'Pin'),
        ('none', 'None'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='specs')
    label = models.CharField(max_length=50)
    value = models.CharField(max_length=200)
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='none')
    icon_text = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
```

**What it does**: Stores the detail rows for an event (Date, Time, Venue, Admission).

**Why a separate model?**: Each event can have multiple specs. Instead of having fixed fields like `date`, `time`, `venue`, we use a flexible system where you can add any number of specs.

**Key concepts:**
- **`ForeignKey`**: Links each spec to one event. Like a child belonging to a parent.
- **`on_delete=models.CASCADE`**: If you delete an event, all its specs are also deleted.
- **`related_name='specs'`**: Lets you access specs from an event using `event.specs.all()`.
- **`choices`**: Restricts the `icon` field to only: calendar, clock, pin, or none.
- **`order`**: Controls the display order (0 = first, 1 = second, etc.).

#### PastEvent Model

```python
class PastEvent(models.Model):
    title = models.CharField(max_length=200)
    event_line = models.CharField(max_length=500)
    event_date = models.DateField()
    is_published = models.BooleanField(default=False)
```

**What it does**: Stores a finished event with a caption and date.

**Why separate from Event?**: Past events have a completely different structure. They have a gallery of photos, not a single flyer. They don't have booking info. So they get their own model.

#### GalleryPhoto Model

```python
class GalleryPhoto(models.Model):
    past_event = models.ForeignKey(PastEvent, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='gallery/')
    alt = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=300, blank=True)
    order = models.IntegerField(default=0)
```

**What it does**: Stores individual photos in a past event's gallery.

**Why a separate model?**: A past event can have many photos. This is the same pattern as EventSpec — one-to-many relationship.

#### HeroSlide Model

```python
class HeroSlide(models.Model):
    image = models.ImageField(upload_to='hero/')
    focus = models.CharField(max_length=50, default='50% 50%')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
```

**What it does**: Stores the hero background images that appear on the homepage.

**Key field**: `focus` — This controls which part of the image is centered. `"74% 50%"` means the focus point is 74% from the left and 50% from the top.

### 4.4 The Admin Panel (`events/admin.py`)

**Location**: `Afronative_admin_sites/events/admin.py`

Django comes with a built-in admin panel. The `admin.py` file customizes how your models look in the admin.

**Key concepts:**

```python
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge', 'ends_at', 'is_published')
    list_filter = ('is_published', 'ends_at')
    search_fields = ('name', 'tagline')
    ordering = ('ends_at',)
```

- **`list_display`**: Which columns to show in the event list table.
- **`list_filter`**: Which filters to show on the right sidebar (e.g., filter by published/unpublished).
- **`search_fields`**: Which fields to search when you type in the search box.
- **`ordering`**: Default sort order (soonest events first).

```python
class EventSpecInline(admin.TabularInline):
    model = EventSpec
    extra = 4
```

- **`TabularInline`**: Shows the inline records as a table (rows) inside the parent page.
- **`extra = 4`**: Shows 4 empty rows by default, so you can quickly add specs without clicking "Add another".

**Why inlines are useful**: Instead of going to a separate page to add specs, you add them right on the event page. It's faster and more intuitive.

### 4.5 The URL Configuration (`afronative/urls.py`)

**Location**: `Afronative_admin_sites/afronative/urls.py`

This file maps URLs to views (functions that handle requests).

```python
from django.urls import path, include
from django.contrib import admin

admin.site.site_header = "AfroNative Admin"

urlpatterns = [
    path('afronative-admin/', admin.site.urls),
    path('api/v1/', include('events.urls')),
]
```

**What each line does:**

- **`admin.site.site_header`**: Changes the admin panel title from "Django administration" to "AfroNative Admin".
- **`path('afronative-admin/', admin.site.urls)`**: Makes the admin available at `/afronative-admin/` instead of `/admin/`.
- **`path('api/v1/', include('events.urls'))`**: Routes all `/api/v1/...` URLs to the `events/urls.py` file.

---

## 5. Phase 2: The JSON API

### 5.1 The API View (`events/api.py`)

**Location**: `Afronative_admin_sites/events/api.py`

This is the bridge between Django and Express. Let's walk through it:

#### Step 1: API Key Authentication

```python
import hmac
from django.conf import settings
from django.http import JsonResponse

def site_content(request):
    # Only allow GET requests
    if request.method != 'GET':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # Check API key
    required_key = getattr(settings, 'SITE_API_KEY', '')
    provided_key = request.headers.get('X-API-Key', '')

    if not hmac.compare_digest(provided_key, required_key):
        return JsonResponse({"error": "Unauthorized"}, status=401)
```

**What it does:**
1. Checks that the request is a GET request (not POST, PUT, DELETE). The API is read-only.
2. Reads the `X-API-Key` header from the request.
3. Compares it with the `SITE_API_KEY` from settings.
4. If they don't match, returns a 401 error.

**Why `hmac.compare_digest`?**
A normal comparison (`==`) is vulnerable to **timing attacks**. Here's how:

- When Python compares two strings with `==`, it stops at the first mismatched character.
- An attacker can measure how long the comparison takes.
- If it takes longer, they know they guessed more characters correctly.
- Over time, they can guess the entire key character by character.

`hmac.compare_digest` always takes the same amount of time, regardless of where the strings differ. This prevents timing attacks.

#### Step 2: Fetch Upcoming Events

```python
from datetime import datetime
from events.models import Event, EventSpec, PastEvent, GalleryPhoto, HeroSlide

# Get upcoming events
upcoming = Event.objects.filter(
    is_published=True,
    ends_at__gt=datetime.now(datetime.timezone)
).order_by('ends_at')

upcoming_events = []
for event in upcoming:
    specs = []
    for spec in event.specs.all().order_by('order'):
        spec_data = {"label": spec.label, "value": spec.value}
        if spec.icon != 'none':
            spec_data["icon"] = spec.icon
        else:
            spec_data["iconText"] = spec.icon_text
        specs.append(spec_data)

    event_data = {
        "name": event.name,
        "tagline": event.tagline,
        "badge": event.badge,
        "endsAt": event.ends_at.isoformat(),
        "flyer": event.flyer.url if event.flyer else "",
        "flyerAlt": event.flyer_alt,
        "specs": specs,
    }

    if event.booking_url:
        event_data["booking"] = {
            "text": event.booking_text,
            "label": event.booking_label,
            "href": event.booking_url,
        }

    upcoming_events.append(event_data)
```

**What it does:**
1. Queries the database for published events where `ends_at` is in the future.
2. Orders them by date (soonest first).
3. For each event, builds a dictionary with all the fields.
4. For each event's specs, builds a specs array.
5. If the event has booking info, adds it to the data.

**Key concepts:**
- **`Event.objects.filter()`**: Django's way of querying the database. It's like SQL's `WHERE` clause.
- **`ends_at__gt=datetime.now()`**: Only events where `ends_at` is greater than now (in the future).
- **`.order_by('ends_at')`**: Sorts results by `ends_at` ascending (soonest first).
- **`event.specs.all()`**: Gets all specs for this event (using the `related_name='specs'` from the ForeignKey).
- **`.isoformat()`**: Converts the datetime to ISO 8601 format (e.g., `"2026-11-16T21:00:00Z"`).

#### Step 3: Fetch Past Event

```python
# Get most recent past event
past = PastEvent.objects.filter(is_published=True).order_by('-event_date').first()

past_event_data = None
if past:
    photos = []
    for photo in past.photos.all().order_by('order'):
        photos.append({
            "src": photo.image.url,
            "alt": photo.alt,
            "caption": photo.caption,
        })

    past_event_data = {
        "eventLine": past.event_line,
        "photos": photos,
    }
```

**What it does:**
1. Gets the most recent published past event.
2. If it exists, builds a dictionary with the event line and all photos.
3. If no past event exists, returns `null`.

**Key concept:**
- **`.order_by('-event_date')`**: The minus sign means descending order (newest first).
- **`.first()`**: Gets only the first result (the most recent).

#### Step 4: Fetch Hero Slides

```python
# Get active hero slides
hero_slides = []
for slide in HeroSlide.objects.filter(is_active=True).order_by('order'):
    hero_slides.append({
        "src": slide.image.url,
        "focus": slide.focus,
    })
```

**What it does:** Gets all active hero slides, ordered by the `order` field.

#### Step 5: Return the JSON Response

```python
response = JsonResponse({
    "upcomingEvents": upcoming_events,
    "pastEvent": past_event_data,
    "heroSlides": hero_slides,
})

# Prevent caching by proxies
response['Cache-Control'] = 'no-store'
return response
```

**What it does:**
1. Wraps all the data in a `JsonResponse` object.
2. Adds a `Cache-Control: no-store` header to prevent intermediate proxies from caching the response.
3. Returns the response to Express.

**Why camelCase keys?**
JavaScript convention uses camelCase (`upcomingEvents`), while Python uses snake_case (`upcoming_events`). We use camelCase in the API to match JavaScript conventions, so Express can use the data directly without conversion.

### 5.2 The API URL (`events/urls.py`)

**Location**: `Afronative_admin_sites/events/urls.py`

```python
from django.urls import path
from .api import site_content

urlpatterns = [
    path('site-content/', site_content, name='site-content'),
]
```

**What it does**: Maps the URL `/api/v1/site-content/` to the `site_content` function.

Combined with the main `urls.py` (`path('api/v1/', include('events.urls'))`), the full URL is:
```
/api/v1/site-content/
```

### 5.3 The Tests (`events/tests.py`)

**Location**: `Afronative_admin_sites/events/tests.py`

Tests are automated checks that verify your code works correctly. We wrote 12 tests:

| Test | What it checks |
|------|---------------|
| `test_401_without_api_key` | Missing key → 401 error |
| `test_401_with_wrong_api_key` | Wrong key → 401 error |
| `test_200_with_correct_api_key` | Correct key → 200 with data |
| `test_unpublished_events_excluded` | Draft events don't appear |
| `test_expired_events_excluded_from_upcoming` | Past events don't appear in upcoming |
| `test_upcoming_events_ordering` | Soonest event comes first |
| `test_past_event_is_most_recent` | Latest past event is returned |
| `test_hero_slides_ordered` | Slides ordered correctly, inactive excluded |
| `test_method_not_allowed` | POST request → 405 error |
| `test_cache_control_header` | Response has `Cache-Control: no-store` |
| `test_event_has_specs` | Specs array is included with icons |
| `test_past_event_photos` | Photos array is included with captions |

**Why tests matter:**
- They catch bugs before your users do
- They let you change code confidently (if a test fails, you know what broke)
- They document expected behavior

---

## 6. Phase 3: Express Website Connection

### 6.1 The Content Service (`src/services/content.js`)

**Location**: `Afro_Naitive/src/services/content.js`

This is the bridge on the Express side. It fetches data from Django and caches it.

#### How the Cache Works

```javascript
let cachedContent = null;
let lastFetchTime = 0;
const CACHE_DURATION = 60000; // 60 seconds
```

- **`cachedContent`**: Stores the last successful response from Django.
- **`lastFetchTime`**: Records when the last fetch happened.
- **`CACHE_DURATION`**: How long the cache is valid (60 seconds).

#### The Fetch Function

```javascript
async function fetchFromDjango() {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    try {
        const response = await fetch(`${DJANGO_API_URL}/api/v1/site-content/`, {
            headers: { 'X-API-Key': SITE_API_KEY },
            signal: controller.signal,
        });
        clearTimeout(timeout);

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('[content.js] Failed to fetch from Django:', error.message);
        return null;
    }
}
```

**What it does:**
1. Creates an `AbortController` — this lets us cancel the request if it takes too long.
2. Sets a 5-second timeout — if Django doesn't respond in 5 seconds, the request is cancelled.
3. Sends a GET request to the Django API with the `X-API-Key` header.
4. If successful, returns the JSON data.
5. If it fails, logs the error and returns `null`.

**Why a timeout?**
Without a timeout, if Django is down, the request would hang forever. The 5-second timeout ensures Express doesn't wait indefinitely.

#### The getContent Function

```javascript
const staticSite = require('../data/site.js');

async function getContent() {
    const now = Date.now();

    // Return cached content if still fresh
    if (cachedContent && (now - lastFetchTime < CACHE_DURATION)) {
        return mergeContent(cachedContent);
    }

    // Fetch fresh content in the background
    fetchFromDjango().then(data => {
        if (data) {
            cachedContent = data;
            lastFetchTime = Date.now();
            console.log('[content.js] Loaded live data from Django API');
        }
    });

    // Return cached or static content
    if (cachedContent) {
        return mergeContent(cachedContent);
    }

    // Fallback to static content
    console.log('[content.js] Falling back to static site.js data');
    return { ...staticSite };
}
```

**What it does:**
1. Checks if the cache is still fresh (less than 60 seconds old).
2. If fresh, returns the cached data immediately.
3. If not fresh, starts a background fetch to update the cache.
4. Returns the cached data (if available) or the static fallback.

**Why background fetch?**
This is called **stale-while-revalidate**. The user gets the cached data immediately (fast), and the cache is updated in the background (fresh for next time). This gives the best of both worlds: speed and freshness.

**Why static fallback?**
If Django is down for the first time (no cache), the site still works with the static data from `site.js`. The site **never breaks** because of Django being down.

#### The Merge Function

```javascript
function mergeContent(djangoData) {
    const merged = { ...staticSite };

    if (djangoData.upcomingEvents && djangoData.upcomingEvents.length > 0) {
        merged.upcoming.events = djangoData.upcomingEvents;
    }

    if (djangoData.pastEvent) {
        merged.pastEvents.eventLine = djangoData.pastEvent.eventLine;
        merged.pastEvents.photos = djangoData.pastEvent.photos;
    }

    if (djangoData.heroSlides && djangoData.heroSlides.length > 0) {
        merged.assets.heroSlides = djangoData.heroSlides;
    }

    return merged;
}
```

**What it does:**
1. Starts with a copy of the static `site.js` data.
2. Replaces specific parts with Django data:
   - `upcoming.events` → Django's `upcomingEvents`
   - `pastEvents.eventLine` and `pastEvents.photos` → Django's `pastEvent`
   - `assets.heroSlides` → Django's `heroSlides`
3. Returns the merged object.

**Why merge instead of replace?**
The static `site.js` has other data that Django doesn't manage (like navigation links, footer text). By merging, we only replace what Django provides and keep everything else from the static file.

### 6.2 The Server Update (`server.js`)

**Location**: `Afro_Naitive/server.js`

The home route was changed from synchronous to asynchronous:

```javascript
const getContent = require('./src/services/content');

app.get('/', async (req, res) => {
    try {
        const site = await getContent();

        // Filter upcoming events to only future ones
        const now = new Date();
        const upcomingEvent = site.upcoming.events?.find(e => new Date(e.endsAt) > now);

        res.render('pages/home', { site, upcomingEvent });
    } catch (error) {
        console.error('Error rendering home:', error);
        res.status(500).send('Server error');
    }
});
```

**What changed:**
- The route is now `async` — it can `await` the `getContent()` function.
- Instead of using the static `site.js` directly, it calls `getContent()` which fetches live data.
- It still filters upcoming events by date (server-side check).
- If anything fails, it returns a 500 error.

**Why `async/await`?**
Fetching data from Django takes time (network request). `async/await` lets the code wait for the fetch to complete without blocking other requests.

### 6.3 The Express `.env` File

**Location**: `Afro_Naitive/.env`

```env
DJANGO_API_URL=http://127.0.0.1:8000
SITE_API_KEY=afronative-secret-api-key-rotate-in-production-32bytes
```

- **`DJANGO_API_URL`**: The URL of your Django server. In production, this will be the Render URL.
- **`SITE_API_KEY`**: The same secret key Django uses. Both must match.

---

## 7. Phase 4: Deployment

The deployment guide (`DEPLOYMENT.md`) covers how to put both apps on the internet using Render. Here's a summary of key concepts:

### What is Render?

**Render** is a cloud hosting platform (like Heroku, Vercel, or Netlify). It hosts your apps on their servers so they're accessible from anywhere.

**Free tier limits:**
- 750 hours/month (enough for 1-2 apps always on)
- 1 GB bandwidth/month
- Services sleep after 15 minutes of inactivity (first request after sleep takes ~30 seconds)

### What is Neon?

**Neon** is a cloud PostgreSQL database. Instead of using SQLite (a file-based database), you use PostgreSQL (a server-based database) for production.

**Why PostgreSQL for production?**
- SQLite is a single file — only one process can write to it at a time.
- PostgreSQL is a server — multiple processes can read and write simultaneously.
- PostgreSQL is more reliable and scalable.

### What is Gunicorn?

**Gunicorn** is a production server for Python web apps. Django's built-in server (`python manage.py runserver`) is for development only. Gunicorn is for production.

**Analogy**: Django's dev server is like a bicycle — great for short trips. Gunicorn is like a car — built for the highway.

### What is WhiteNoise?

**WhiteNoise** serves static files (CSS, JS, images) from Django in production. Normally, you'd use a separate server (like Nginx) for static files, but WhiteNoise lets Django handle it.

---

## 8. How to Run Everything Locally

### Step 1: Start Django

```powershell
cd C:\Users\SHARP\Desktop\Afronative_admin_sites
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

Django will be available at: `http://127.0.0.1:8000/`
Admin panel at: `http://127.0.0.1:8000/afronative-admin/`

### Step 2: Start Express

```powershell
cd C:\Users\SHARP\Desktop\Afro_Naitive
node server.js
```

Express will be available at: `http://localhost:3000`

### Step 3: Test the Connection

1. Open `http://localhost:3000` in your browser
2. Check the Express terminal for: `[content.js] Loaded live data from Django API`
3. Add an event in the Django admin
4. Wait up to 60 seconds
5. Refresh the Express site — your event should appear

---

## 9. Common Questions

### Q: Why can't I see my event on the Express site immediately?

**A**: The cache lasts 60 seconds. After you add an event in Django, wait up to 60 seconds before refreshing the Express site. You can also restart the Express server to clear the cache.

### Q: What if I forget my admin password?

**A**: Run this command in your Django project:
```powershell
python manage.py changepassword Code_crush
```

### Q: How do I add a new event?

**A**:
1. Go to `http://127.0.0.1:8000/afronative-admin/`
2. Log in with your admin credentials
3. Click **Events** → **Add Event**
4. Fill in the details
5. Add specs in the inline section
6. Check "Published"
7. Click "Save"

### Q: How do I move an event from upcoming to past?

**A**: You don't need to manually move it! The API automatically filters events:
- Events with `ends_at` in the future → appear in `upcomingEvents`
- Events with `ends_at` in the past → don't appear in `upcomingEvents`

For the past event gallery, you create a separate `PastEvent` with photos.

### Q: What's the difference between `Event` and `PastEvent`?

**A**:
- **Event** = An upcoming event with a flyer, specs, and booking info
- **PastEvent** = A finished event with a gallery of photos

They're separate because they have different data structures. An upcoming event needs booking info; a past event needs a photo gallery.

### Q: How do I change the API key?

**A**:
1. Generate a new key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Update `SITE_API_KEY` in Django's `.env`
3. Update `SITE_API_KEY` in Express's `.env`
4. Restart both servers

### Q: Why does my image show a broken link?

**A**: Check that:
1. `CLOUDINARY_URL` is correctly set in Django's `.env`
2. The format is: `cloudinary://API_KEY:API_SECRET@CLOUD_NAME`
3. Your Cloudinary account is active

### Q: Can I use this without Cloudinary?

**A**: Yes! If you remove the Cloudinary settings, Django will store images locally in the `media/` folder. But for production, Cloudinary is recommended because it handles scaling, optimization, and delivery.

---

## 🎓 Summary

You've built a complete two-app system:

1. **Django Admin** — Where you manage events, upload images, and control content
2. **JSON API** — The secure bridge that sends data from Django to Express
3. **Express Website** — The public-facing site that displays your events
4. **Cloudinary** — Cloud storage for your images
5. **Caching** — 60-second cache for performance
6. **Fallback** — Static data as backup if Django is down

This is real-world architecture used by professional developers. Keep learning, keep building! 🚀
