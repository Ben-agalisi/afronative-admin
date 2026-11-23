from django.contrib import admin
from .models import Event, EventSpec, PastEvent, GalleryPhoto, HeroSlide


# ---------------------------------------------------------------------------
# Inline — EventSpec rows inside the Event edit page
# ---------------------------------------------------------------------------

class EventSpecInline(admin.TabularInline):
    model = EventSpec
    extra = 4  # Show 4 empty rows by default (Date, Time, Venue, Admission)
    fields = ('order', 'icon', 'icon_text', 'label', 'value')
    list_display = ('order', 'icon', 'label', 'value')


# ---------------------------------------------------------------------------
# Inline — GalleryPhoto rows inside the PastEvent edit page
# ---------------------------------------------------------------------------

class GalleryPhotoInline(admin.TabularInline):
    model = GalleryPhoto
    extra = 2  # Show 2 empty rows by default
    fields = ('order', 'image', 'alt', 'caption')
    list_display = ('order', 'caption', 'image')


# ---------------------------------------------------------------------------
# Event Admin
# ---------------------------------------------------------------------------

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin for managing upcoming and past events."""

    inlines = [EventSpecInline]  # EventSpecs appear inside Event edit page
    list_display = ('name', 'badge', 'ends_at', 'is_upcoming', 'is_published', 'created_at')
    list_filter = ('is_published', 'ends_at', 'created_at')
    search_fields = ('name', 'tagline', 'booking_text')
    date_hierarchy = 'ends_at'
    fieldsets = (
        ('Event Details', {
            'fields': ('name', 'tagline', 'badge', 'ends_at')
        }),
        ('Flyer Image', {
            'fields': ('flyer', 'flyer_alt'),
            'description': 'Upload the event flyer — it will be sent to Cloudinary automatically.',
        }),
        ('Booking Info', {
            'fields': ('booking_text', 'booking_label', 'booking_url'),
        }),
        ('Status', {
            'fields': ('is_published',),
            'description': 'Only published events appear on the website.',
        }),
    )


# ---------------------------------------------------------------------------
# PastEvent Admin
# ---------------------------------------------------------------------------

@admin.register(PastEvent)
class PastEventAdmin(admin.ModelAdmin):
    """Admin for managing past event galleries."""

    inlines = [GalleryPhotoInline]  # Gallery photos appear inside PastEvent edit page
    list_display = ('title', 'event_date', 'is_published', 'created_at')
    list_filter = ('is_published', 'event_date', 'created_at')
    search_fields = ('title', 'event_line')
    date_hierarchy = 'event_date'
    fieldsets = (
        ('Event Info', {
            'fields': ('title', 'event_line', 'event_date')
        }),
        ('Status', {
            'fields': ('is_published',),
            'description': 'Only published past events appear on the website.',
        }),
    )


# ---------------------------------------------------------------------------
# HeroSlide Admin
# ---------------------------------------------------------------------------

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    """Admin for managing hero background images."""

    list_display = ('order', 'image_thumbnail', 'focus', 'is_active', 'created_at')
    list_filter = ('is_active',)
    ordering = ['order']
    fieldsets = (
        ('Slide', {
            'fields': ('image', 'focus', 'order', 'is_active'),
            'description': 'Hero background images rotate on the homepage. Focus controls cropping on mobile.',
        }),
    )

    def image_thumbnail(self, obj):
        """Show a small thumbnail preview in the admin list."""
        if obj.image:
            return f'<img src="{obj.image.url}" style="width:100px;height:auto;" />'
        return '—'
    image_thumbnail.short_description = 'Preview'
    image_thumbnail.allow_tags = True


# ---------------------------------------------------------------------------
# Custom admin site title
# ---------------------------------------------------------------------------

admin.site.site_header = 'AfroNative Admin'
admin.site.site_title = 'AfroNative Admin Portal'
admin.site.index_title = 'Welcome to AfroNative Admin — Manage your events, galleries, and hero slides.'
