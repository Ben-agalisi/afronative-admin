"""
Django settings for afronative project.

All sensitive values come from environment variables (.env file).
Never hardcode secrets in this file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Security settings — from env vars
# ---------------------------------------------------------------------------

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fallback-change-in-production')

# DEBUG should be False in production
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# Comma-separated list of allowed hostnames
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'events',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'afronative.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Custom admin templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'afronative.wsgi.application'


# ---------------------------------------------------------------------------
# Database — SQLite in dev, Postgres in production (via DATABASE_URL)
# ---------------------------------------------------------------------------

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')

if DATABASE_URL.startswith('sqlite'):
    # Local development with SQLite
    db_path = DATABASE_URL.replace('sqlite:///', '')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / db_path,
        }
    }
else:
    # Production with Postgres (parse the DATABASE_URL)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------------------------
# Static files (CSS, JavaScript, images)
# ---------------------------------------------------------------------------

STATIC_URL = 'static/'

# Directory where collectstatic will gather all static files
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Additional directories for custom static files (admin styling)
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Whitenoise serves static files efficiently in production
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# ---------------------------------------------------------------------------
# Cloudinary — image storage
# ---------------------------------------------------------------------------
# CLOUDINARY_URL format: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
# If not set, falls back to local media folder for development

CLOUDINARY_URL = os.getenv('CLOUDINARY_URL', '')

if CLOUDINARY_URL:
    # Parse CLOUDINARY_URL manually and configure the cloudinary SDK
    # Format: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
    # IMPORTANT: urlparse() lowercases the hostname, but Cloudinary cloud names
    # are case-sensitive! Extract the cloud name from the raw string instead.
    import cloudinary
    from urllib.parse import urlparse

    parsed = urlparse(CLOUDINARY_URL)
    api_key = parsed.username
    api_secret = parsed.password

    # Extract cloud name with original case from the raw URL string
    # urlparse lowercases hostname, so we parse manually
    if '@' in CLOUDINARY_URL:
        cloud_name = CLOUDINARY_URL.split('@')[-1]
    else:
        cloud_name = parsed.hostname

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,  # Force HTTPS URLs
    )

    # Use Cloudinary for image storage (Django 5+ STORAGES setting)
    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
else:
    # Fallback to local media folder (Django 5+ STORAGES setting)
    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }
    MEDIA_URL = '/media/'


# ---------------------------------------------------------------------------
# API Security — secret key for Express to fetch data from Django
# ---------------------------------------------------------------------------

SITE_API_KEY = os.getenv('SITE_API_KEY', '')

# ---------------------------------------------------------------------------
# CSRF trusted origins (for production API calls from Express)
# ---------------------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    origin for origin in os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost:3000').split(',')
    if origin.strip()
]


# ---------------------------------------------------------------------------
# Production security — only when DEBUG is False
# ---------------------------------------------------------------------------

if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}
