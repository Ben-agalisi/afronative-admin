"""
URL configuration for afronative project.

Admin URL comes from the ADMIN_URL environment variable for security.
API endpoints are included under /api/v1/.
"""
import os
from dotenv import load_dotenv
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Load .env file so ADMIN_URL is available here (settings.py also loads it)
load_dotenv()

# Read admin URL from env var (default to 'admin/' for backwards compatibility)
admin_url = os.getenv('ADMIN_URL', 'admin/').strip('/') + '/'

def root_view(request):
    """Simple landing page for the root URL."""
    return HttpResponse(
        "<html><body style='font-family: Arial, sans-serif; text-align: center; "
        "padding: 50px; background: #1a1a2e; color: #FFD700;'>"
        "<h1>AfroNative Admin Backend</h1>"
        "<p>API is running. Visit <a href='/afronative-admin/' style='color: #FFD700;'>Admin Panel</a> to manage content.</p>"
        "</body></html>",
        content_type='text/html'
    )

urlpatterns = [
    path('', root_view, name='root'),
    path(admin_url, admin.site.urls),
    # Read-only API for the Express website
    path('api/v1/', include('events.urls')),
]

# Serve static files (CSS, JS) during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
