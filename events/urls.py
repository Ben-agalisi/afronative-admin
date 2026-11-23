"""
URL routing for the events app API.

All public API endpoints live here. The admin panel uses Django's
built-in admin URLs, which are configured in afronative/urls.py.
"""
from django.urls import path
from . import api

urlpatterns = [
    path('site-content/', api.site_content, name='site-content'),
]
