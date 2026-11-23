"""
Read-only JSON API for the Express website.

The Express site fetches data from this endpoint to display events,
past event galleries, and hero slides. Only published items are included.
Security: Requires X-API-Key header matching SITE_API_KEY env var.
"""

import hmac
from django.conf import settings
from django.http import JsonResponse, HttpRequest
from django.utils import timezone
from .models import Event, EventSpec, PastEvent, GalleryPhoto, HeroSlide


def get_cloud_name():
    """
    Extract the Cloudinary cloud name from settings.CLOUDINARY_URL.
    
    Format: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
    Returns the cloud name or None if not configured.
    """
    cloudinary_url = getattr(settings, 'CLOUDINARY_URL', '')
    if not cloudinary_url or '@' not in cloudinary_url:
        return None
    # Extract cloud name after the @ symbol
    return cloudinary_url.split('@')[-1]


def to_absolute_image_url(image_field):
    """
    Convert an image field to an absolute HTTPS URL.
    
    If the image is already a Cloudinary URL (starts with https://), return it as-is.
    If it's a local relative path (e.g., /event_flyers/photo.jpg), construct a
    Cloudinary URL from it so the Express site can load it from Cloudinary.
    
    This handles both new uploads (already Cloudinary URLs) and old uploads
    (local paths that need to be converted).
    """
    if not image_field:
        return ""
    
    url = image_field.url
    
    # If already an absolute URL (Cloudinary or other), return as-is
    if url.startswith('http://') or url.startswith('https://'):
        # Ensure HTTPS for Cloudinary URLs
        if url.startswith('http://'):
            url = 'https://' + url[7:]
        return url
    
    # It's a relative path like /event_flyers/photo.jpg
    # Construct a Cloudinary URL: https://res.cloudinary.com/{cloud_name}/image/upload/{path}
    cloud_name = get_cloud_name()
    if not cloud_name:
        return url  # Fallback: return the relative path if Cloudinary is not configured
    
    # Remove leading slash from the path
    public_id = url.lstrip('/')
    
    # Build the Cloudinary URL
    cloudinary_url = f'https://res.cloudinary.com/{cloud_name}/image/upload/{public_id}'
    return cloudinary_url


def site_content(request: HttpRequest) -> JsonResponse:
    """
    GET /api/v1/site-content/

    Returns JSON matching the shape of src/data/site.js in the Express app:
    {
      "upcomingEvents": [ ... ],
      "pastEvent": { ... } | null,
      "heroSlides": [ ... ]
    }

    Rules:
    - Only published/active items.
    - upcomingEvents: ends_at in the future, soonest first.
    - pastEvent: most recent published past event (or null).
    - Requires X-API-Key header. Returns 401 if missing or wrong.
    - GET only. Returns 405 for other methods.
    - Sends Cache-Control: no-store (no caching by intermediaries).
    """

    # -----------------------------------------------------------------------
    # Method check — only GET allowed
    # -----------------------------------------------------------------------
    if request.method != 'GET':
        return JsonResponse(
            {"error": "Method not allowed. Use GET."},
            status=405,
        )

    # -----------------------------------------------------------------------
    # API key authentication — server-to-server secret
    # -----------------------------------------------------------------------
    required_key = getattr(settings, 'SITE_API_KEY', '')
    provided_key = request.headers.get('X-API-Key', '')

    # Use hmac.compare_digest to prevent timing attacks
    if not hmac.compare_digest(provided_key, required_key):
        return JsonResponse(
            {"error": "Unauthorized. Invalid or missing API key."},
            status=401,
        )

    # -----------------------------------------------------------------------
    # Build upcoming events
    # -----------------------------------------------------------------------
    now = timezone.now()
    upcoming_qs = Event.objects.filter(
        is_published=True,
        ends_at__gt=now,  # Only future events
    ).order_by('ends_at')  # Soonest first

    upcoming_events = []
    for event in upcoming_qs:
        # Build specs array, ordered by 'order' field
        specs = []
        for spec in event.specs.all():
            spec_dict = {
                "label": spec.label,
                "value": spec.value,
            }
            if spec.icon and spec.icon != 'none':
                spec_dict["icon"] = spec.icon
            if spec.icon_text:
                spec_dict["iconText"] = spec.icon_text
            specs.append(spec_dict)

        # Build booking object (only if there's a URL)
        booking = None
        if event.booking_url:
            booking = {
                "text": event.booking_text,
                "label": event.booking_label,
                "href": event.booking_url,
            }

        event_dict = {
            "name": event.name,
            "tagline": event.tagline,
            "badge": event.badge,
            "endsAt": event.ends_at.isoformat(),  # ISO 8601 UTC format
            "flyer": to_absolute_image_url(event.flyer),
            "flyerAlt": event.flyer_alt,
            "specs": specs,
        }
        if booking:
            event_dict["booking"] = booking

        upcoming_events.append(event_dict)

    # -----------------------------------------------------------------------
    # Build past event (most recent published one)
    # -----------------------------------------------------------------------
    past_event_data = None
    past_qs = PastEvent.objects.filter(
        is_published=True,
    ).order_by('-event_date')  # Most recent first

    if past_qs.exists():
        past = past_qs.first()
        # Build photos array, ordered by 'order' field
        photos = []
        for photo in past.photos.all():
            photos.append({
                "src": to_absolute_image_url(photo.image),
                "alt": photo.alt,
                "caption": photo.caption,
            })

        past_event_data = {
            "eventLine": past.event_line,
            "photos": photos,
        }

    # -----------------------------------------------------------------------
    # Build hero slides
    # -----------------------------------------------------------------------
    hero_slides = []
    for slide in HeroSlide.objects.filter(is_active=True).order_by('order'):
        slide_dict = {
            "src": to_absolute_image_url(slide.image),
        }
        if slide.focus and slide.focus != '50% 50%':
            slide_dict["focus"] = slide.focus
        hero_slides.append(slide_dict)

    # -----------------------------------------------------------------------
    # Assemble and return the final JSON
    # -----------------------------------------------------------------------
    response = JsonResponse({
        "upcomingEvents": upcoming_events,
        "pastEvent": past_event_data,
        "heroSlides": hero_slides,
    })

    # Prevent intermediaries from caching sensitive content
    response['Cache-Control'] = 'no-store'
    return response
