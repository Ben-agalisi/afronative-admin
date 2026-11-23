"""
Management command to add a hero slide image from a local file.

Usage:
    python manage.py add_hero_slide hero_slides/hero_bg_2.webp
    python manage.py add_hero_slide hero_slides/hero_bg_2.webp --order 1
    python manage.py add_hero_slide hero_slides/hero_bg_2.webp --inactive
"""
from django.core.management.base import BaseCommand
from django.core.files import File
from events.models import HeroSlide
import os


class Command(BaseCommand):
    help = 'Add a hero slide from a local image file, uploading it to Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the image file (relative to project root)',
        )
        parser.add_argument(
            '--order',
            type=int,
            default=None,
            help='Display order (default: auto-increment after last slide)',
        )
        parser.add_argument(
            '--inactive',
            action='store_true',
            help='Create as inactive (default: active)',
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        order = options['order']
        is_active = not options['inactive']

        if not os.path.exists(file_path):
            self.stderr.style.ERROR(
                f'Error: File not found: {file_path}'
            )
            return

        # Determine order: auto-increment if not specified
        if order is None:
            last = HeroSlide.objects.order_by('-order').first()
            order = (last.order + 1) if last else 1

        # Create the slide and save the image file
        slide = HeroSlide.objects.create(
            order=order,
            is_active=is_active,
        )

        with open(file_path, 'rb') as f:
            file_name = os.path.basename(file_path)
            slide.image.save(file_name, File(f), save=True)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created hero slide #{slide.id} '
                f'(order={order}, active={is_active})\n'
                f'Cloudinary URL: {slide.image.url}'
            )
        )
