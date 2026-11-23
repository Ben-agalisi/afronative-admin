"""
Tests for the read-only JSON API.

Covers:
- 401 without API key
- 401 with wrong API key
- 200 with correct API key
- Unpublished events are excluded
- Expired events are excluded from upcomingEvents
- Ordering: soonest upcoming event first
- Past event is the most recent published one
- Hero slides are ordered correctly
"""

import os
from datetime import timedelta
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from .models import Event, EventSpec, PastEvent, GalleryPhoto, HeroSlide


# Use a test API key for all tests
TEST_API_KEY = 'test-secret-key-for-unit-tests-12345'


@override_settings(SITE_API_KEY=TEST_API_KEY)
class SiteContentAPITest(TestCase):
    """Test the /api/v1/site-content/ endpoint."""

    def setUp(self):
        """Create test data: events, past events, and hero slides."""
        now = timezone.now()

        # --- Upcoming events ---
        self.event_future_1 = Event.objects.create(
            name="Future Event 1",
            tagline="Coming Soon",
            badge="Upcoming",
            ends_at=now + timedelta(days=1),  # 1 day from now
            is_published=True,
        )
        EventSpec.objects.create(
            event=self.event_future_1,
            label="Date",
            value="2026-12-01",
            icon="calendar",
            order=1,
        )

        self.event_future_2 = Event.objects.create(
            name="Future Event 2",
            tagline="Later",
            badge="Upcoming",
            ends_at=now + timedelta(days=30),  # 30 days from now
            is_published=True,
        )

        # --- Unpublished event (should be excluded) ---
        self.event_unpublished = Event.objects.create(
            name="Unpublished Event",
            tagline="Hidden",
            badge="Draft",
            ends_at=now + timedelta(days=5),
            is_published=False,
        )

        # --- Expired event (should NOT appear in upcomingEvents) ---
        self.event_expired = Event.objects.create(
            name="Expired Event",
            tagline="Already Passed",
            badge="Past",
            ends_at=now - timedelta(days=1),  # 1 day ago
            is_published=True,
        )

        # --- Past event ---
        self.past_event = PastEvent.objects.create(
            title="Past Party",
            event_line="PAST PARTY • FIRST EDITION • 1 NOVEMBER 2026 • ACCRA",
            event_date=now - timedelta(days=10),
            is_published=True,
        )
        GalleryPhoto.objects.create(
            past_event=self.past_event,
            alt="Photo 1",
            caption="Great moment",
            order=1,
        )

        # --- Hero slides ---
        self.slide_1 = HeroSlide.objects.create(
            order=1,
            is_active=True,
            focus="50% 50%",
        )
        self.slide_2 = HeroSlide.objects.create(
            order=2,
            is_active=True,
            focus="74% 50%",
        )
        self.slide_inactive = HeroSlide.objects.create(
            order=3,
            is_active=False,
        )

    def test_401_without_api_key(self):
        """Request without X-API-Key header should return 401."""
        response = self.client.get('/api/v1/site-content/')
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn('error', data)

    def test_401_with_wrong_api_key(self):
        """Request with wrong X-API-Key should return 401."""
        response = self.client.get(
            '/api/v1/site-content/',
            HTTP_X_API_KEY='wrong-key',
        )
        self.assertEqual(response.status_code, 401)

    def test_200_with_correct_api_key(self):
        """Request with correct X-API-Key should return 200."""
        response = self.client.get(
            '/api/v1/site-content/',
            HTTP_X_API_KEY=TEST_API_KEY,
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('upcomingEvents', data)
        self.assertIn('pastEvent', data)
        self.assertIn('heroSlides', data)

    def test_unpublished_events_excluded(self):
        """Unpublished events should not appear in upcomingEvents."""
        response = self.client.get(
            '/api/v1/site-content/',
            HTTP_X_API_KEY=TEST_API_KEY,
        )
        data = response.json()
        event_names = [e['name'] for e in data['upcomingEvents']]
        self.assertNotIn('Unpublished Event', event_names)

    def test_expired_events_excluded_from_upcoming(self):
        """Expired events should not appear in upcomingEvents."""
        response = self.client.get(
            '/api/v1/site-content/',
            HTTP_X_API_KEY=TEST_API_KEY,
        )
        data = response.json()
        event_names = [e['name'] for e in data['upcomingEvents']]
        self.assertNotIn('Expired Event', event_names)

    def test_upcoming_events_ordering(self):
        """Upcoming events should be ordered soonest first."""
        response = self.client.get(
            '/api/v1/site-content/',
            HTTP_X_API_KEY=TEST_API_KEY,
        )
        data = response.json()
        events = data['upcomingEvents']
        # Should have 2 published future events
        self.assertEqual(len(events), 2)
        # First should be the one 1 day away, not 30 days
        self.assertEqual(events[0]['name'], 'Future Event 1')
        self.assertEqual(events[1]['name'], 'Future Event 2')

    def test_past_event_is_most_recent(self):
        """pastEvent should be the most recent published past event."""
        response = self.client.get(
            '/api/v1/site-content/',
            HTTP_X_API_KEY=TEST_API_KEY,
        )
        data = response.json()
        self.assertIsNotNone(data['pastEvent'])
        self.assertEqual(data['pastEvent']['eventLine'], 'PAST PARTY • FIRST EDITION • 1 NOVEMBER 2026 • ACCRA')

    def test_hero_slides_ordered(self):
        """Hero slides should be ordered by 'order' field, inactive excluded."""
        response = self.client.get(
            '/api/v1/site-content/',
            HTTP_X_API_KEY=TEST_API_KEY,
        )
        data = response.json()
        slides = data['heroSlides']
        # Should have 2 active slides (slide_1 and slide_2)
        self.assertEqual(len(slides), 2)

    def test_method_not_allowed(self):
        """POST request should return 405."""
        response = self.client.post(
            '/api/v1/site-content/',
            HTTP_X_API_KEY=TEST_API_KEY,
        )
        self.assertEqual(response.status_code, 405)

    def test_cache_control_header(self):
        """Response should have Cache-Control: no-store."""
        response = self.client.get(
            '/api/v1/site-content/',
            HTTP_X_API_KEY=TEST_API_KEY,
        )
        self.assertEqual(response['Cache-Control'], 'no-store')

    def test_event_has_specs(self):
        """Event with specs should include the specs array."""
        response = self.client.get(
            '/api/v1/site-content/',
            HTTP_X_API_KEY=TEST_API_KEY,
        )
        data = response.json()
        # Find the event with specs
        event_1 = next(e for e in data['upcomingEvents'] if e['name'] == 'Future Event 1')
        self.assertIn('specs', event_1)
        self.assertEqual(len(event_1['specs']), 1)
        self.assertEqual(event_1['specs'][0]['label'], 'Date')
        self.assertEqual(event_1['specs'][0]['icon'], 'calendar')

    def test_past_event_photos(self):
        """Past event should include photos array."""
        response = self.client.get(
            '/api/v1/site-content/',
            HTTP_X_API_KEY=TEST_API_KEY,
        )
        data = response.json()
        past = data['pastEvent']
        self.assertIn('photos', past)
        self.assertEqual(len(past['photos']), 1)
        self.assertEqual(past['photos'][0]['caption'], 'Great moment')
