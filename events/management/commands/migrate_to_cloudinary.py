"""
Management command to upload local images to Cloudinary and update database records.

This command finds images that were saved to local folders (before Cloudinary was configured)
and re-uploads them to Cloudinary, updating the database with the new Cloudinary URLs.

Usage:
    python manage.py migrate_to_cloudinary

This will:
1. Upload event flyers from local folders to Cloudinary
2. Upload hero slides from local folders to Cloudinary
3. Create HeroSlide database records for local hero slide files
4. Update Event database records with Cloudinary URLs

Run this once to migrate your existing images to Cloudinary.
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from events.models import Event, HeroSlide
import cloudinary
from cloudinary.uploader import upload


class Command(BaseCommand):
    help = 'Migrate local images to Cloudinary and update database records'

    def handle(self, *args, **options):
        self.stdout.write('Starting migration to Cloudinary...')
        
        # Verify Cloudinary is configured
        # Note: Cloudinary cloud names are case-sensitive!
        # The urlparse may lowercase the hostname, so we need to preserve the original case
        cloud_name = cloudinary.config().cloud_name
        if not cloud_name:
            self.stdout.write(self.style.ERROR('Cloudinary is not configured. Check CLOUDINARY_URL in .env'))
            return
        
        # Fix: cloudinary.config() may lowercase the cloud_name from urlparse
        # Read the original CLOUDINARY_URL to get the correct case
        original_url = settings.CLOUDINARY_URL
        if original_url:
            # Extract cloud name with original case from the URL
            # Format: cloudinary://API_KEY:API_SECRET@CLOUD_NAME
            from urllib.parse import urlparse
            parsed = urlparse(original_url)
            # urlparse lowercases hostname, so extract from the raw string instead
            if '@' in original_url:
                cloud_name = original_url.split('@')[-1]
        
        self.stdout.write(f'Cloudinary cloud: {cloud_name}')
        
        # Re-configure Cloudinary with the correct case
        if cloud_name != cloudinary.config().cloud_name:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=cloudinary.config().api_key,
                api_secret=cloudinary.config().api_secret,
                secure=True,
            )
        
        # Get the media root (where local files are stored)
        media_root = settings.BASE_DIR / 'event_flyers'
        hero_root = settings.BASE_DIR / 'hero_slides'
        
        # -----------------------------------------------------------------------
        # Step 1: Upload event flyers to Cloudinary
        # -----------------------------------------------------------------------
        self.stdout.write('\n--- Migrating Event Flyers ---')
        
        events = Event.objects.filter(flyer__isnull=False)
        for event in events:
            local_path = event.flyer.path
            
            if os.path.exists(local_path):
                self.stdout.write(f'Uploading event flyer: {event.flyer.name}')
                
                try:
                    # Upload to Cloudinary
                    result = upload(
                        local_path,
                        folder='event_flyers',
                        public_id=event.flyer.name.replace(os.sep, '/').lstrip('/').rsplit('/', 1)[-1].rsplit('.', 1)[0],
                        overwrite=True,
                    )
                    
                    # Update the event with the Cloudinary URL
                    event.flyer.name = result['public_id']
                    event.save()
                    
                    self.stdout.write(self.style.SUCCESS(f'  [OK] Uploaded: {result["secure_url"]}'))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  [FAIL] Failed: {e}'))
            else:
                self.stdout.write(f'  [WARN] File not found: {local_path}')
        
        # -----------------------------------------------------------------------
        # Step 2: Upload hero slides from local folder to Cloudinary
        # -----------------------------------------------------------------------
        self.stdout.write('\n--- Migrating Hero Slides ---')
        
        if hero_root.exists():
            hero_files = list(hero_root.glob('*'))
            hero_files = [f for f in hero_files if f.is_file()]
            
            for hero_file in hero_files:
                # Check if this file is already associated with a HeroSlide
                file_name = hero_file.name
                # Simple check: see if any slide has this file name in its image path
                existing_slide = None
                for slide in HeroSlide.objects.all():
                    if slide.image and file_name in str(slide.image):
                        existing_slide = slide
                        break
                
                if existing_slide:
                    self.stdout.write(f'Slide already exists: {file_name}')
                    continue
                
                self.stdout.write(f'Uploading hero slide: {file_name}')
                
                try:
                    # Upload to Cloudinary
                    public_id = f'hero_slides/{hero_file.stem}'
                    result = upload(
                        str(hero_file),
                        folder='hero_slides',
                        public_id=hero_file.stem,
                        overwrite=True,
                    )
                    
                    # Create HeroSlide record
                    slide = HeroSlide.objects.create(
                        image=result['public_id'],
                        is_active=True,
                        order=HeroSlide.objects.count() + 1,
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f'  [OK] Uploaded: {result["secure_url"]}'))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  [FAIL] Failed: {e}'))
        else:
            self.stdout.write('  No hero_slides folder found')
        
        # -----------------------------------------------------------------------
        # Summary
        # -----------------------------------------------------------------------
        self.stdout.write('\n--- Migration Complete ---')
        self.stdout.write(f'Events with flyers: {Event.objects.filter(flyer__isnull=False).count()}')
        self.stdout.write(f'Hero slides: {HeroSlide.objects.count()}')
        self.stdout.write(self.style.SUCCESS('Migration finished!'))
