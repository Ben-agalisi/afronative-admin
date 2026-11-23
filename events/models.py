from django.db import models
from django.utils import timezone


class Event(models.Model):
    """
    Upcoming or past event with flyer, specs, and booking info.
    Matches the 'upcoming.events' array shape in site.js.
    """
    name = models.CharField(max_length=200, help_text="Event name, e.g. 'PÁRTI EISAGÓSIS'")
    tagline = models.CharField(max_length=300, blank=True, default='', help_text="Subtitle, e.g. 'TODAY WE PARTI • FIRST EDITION'")
    badge = models.CharField(max_length=200, default='Current Official Edition', help_text="Badge shown above the event name")
    ends_at = models.DateTimeField(help_text="When the event ends (UTC). Used to auto-move to past events.")
    flyer = models.ImageField(upload_to='event_flyers/', help_text="Main flyer image — uploaded to Cloudinary")
    flyer_alt = models.CharField(max_length=300, blank=True, default='', help_text="Alt text for the flyer image (accessibility)")

    # Booking fields
    booking_text = models.CharField(max_length=300, blank=True, default='', help_text="Text above the booking button, e.g. 'DM us on Instagram...'")
    booking_label = models.CharField(max_length=200, blank=True, default='', help_text="Button label, e.g. 'Message on Instagram'")
    booking_url = models.URLField(blank=True, default='', help_text="Booking or contact URL")

    # Status
    is_published = models.BooleanField(default=False, help_text="Only published events appear on the website")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ends_at']  # Soonest first

    def __str__(self):
        return self.name

    def is_upcoming(self):
        """Event is still happening or hasn't happened yet."""
        return self.ends_at > timezone.now()

    def is_past(self):
        """Event has finished."""
        return self.ends_at <= timezone.now()


class EventSpec(models.Model):
    """
    Inline detail row for an event (Date, Time, Venue, Admission, etc.).
    Matches the 'specs' array inside each event in site.js.
    """
    ICON_CHOICES = [
        ('calendar', 'Calendar'),
        ('clock', 'Clock'),
        ('pin', 'Pin/Location'),
        ('none', 'None (use iconText instead)'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='specs', help_text="Parent event")
    label = models.CharField(max_length=100, help_text="Label, e.g. 'Date', 'Time', 'Venue'")
    value = models.CharField(max_length=300, help_text="Value, e.g. '07.11.2026', '6:00 PM Onwards'")
    icon = models.CharField(max_length=20, choices=ICON_CHOICES, default='none', help_text="Icon name — must match icon.ejs")
    icon_text = models.CharField(max_length=50, blank=True, default='', help_text="Text shown instead of icon when icon='none', e.g. '18+'")
    order = models.PositiveIntegerField(default=0, help_text="Display order (smaller = first)")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.event.name} — {self.label}"


class PastEvent(models.Model):
    """
    A finished event with a photo gallery.
    Matches the 'pastEvents' object in site.js.
    """
    title = models.CharField(max_length=200, help_text="Internal title for this past event")
    event_line = models.CharField(
        max_length=500,
        help_text="One-line caption shown above the gallery, e.g. 'PÁRTI EISAGÓSIS • FIRST EDITION • 7 NOVEMBER 2026 • THE KOVE, ACCRA'"
    )
    event_date = models.DateField(help_text="When this event happened (for sorting)")
    is_published = models.BooleanField(default=False, help_text="Only published past events appear on the website")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-event_date']  # Most recent first

    def __str__(self):
        return self.title


class GalleryPhoto(models.Model):
    """
    Inline photo for a past event gallery.
    Matches the 'photos' array inside pastEvents in site.js.
    """
    past_event = models.ForeignKey(PastEvent, on_delete=models.CASCADE, related_name='photos', help_text="Parent past event")
    image = models.ImageField(upload_to='gallery_photos/', help_text="Photo — uploaded to Cloudinary")
    alt = models.CharField(max_length=300, blank=True, default='', help_text="Alt text for accessibility")
    caption = models.CharField(max_length=300, blank=True, default='', help_text="Short caption shown on hover")
    order = models.PositiveIntegerField(default=0, help_text="Display order (smaller = first)")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.past_event.title} — {self.caption or 'Photo'}"


class HeroSlide(models.Model):
    """
    Hero background image for the homepage slider.
    Matches the 'assets.heroSlides' array in site.js.
    """
    image = models.ImageField(upload_to='hero_slides/', help_text="Hero background image — uploaded to Cloudinary")
    focus = models.CharField(
        max_length=50,
        default='50% 50%',
        blank=True,
        help_text="CSS background-position for cropping on mobile, e.g. '74% 50%'"
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order (smaller = first)")
    is_active = models.BooleanField(default=True, help_text="Only active slides appear on the website")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Hero slide #{self.order}"
