#!/usr/bin/env python
import os
import sys
from django.core.files import File
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'embracingmain.settings')
django.setup()

from main.models import Post

def migrate_images():
    print("Starting media migration to Cloudinary...")
    count = {'success': 0, 'skipped': 0, 'error': 0}
    
    # Get all posts with images
    posts = Post.objects.filter(image__isnull=False)
    total = posts.count()
    print(f"Found {total} posts with images")
    
    for i, post in enumerate(posts, 1):
        print(f"\nProcessing {i}/{total}: {post.title}")
        try:
            # If URL is already a remote URL (Cloudinary), skip it
            url = getattr(post.image, 'url', '')
            if url.startswith('http'):
                print(f"→ Skipping (already remote): {url}")
                count['skipped'] += 1
                continue

            # Get local file path
            # Get file name from the URL
            url = str(post.image)
            fname = os.path.basename(url)
            # Look in static/media directory
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'static', 'media', 'post_images', fname)
            if not os.path.exists(path):
                print(f"→ Error: File not found at: {path}")
                count['error'] += 1
                continue

            if not os.path.exists(path):
                print(f"→ File not found locally: {path}")
                count['error'] += 1
                continue

            # Read local file and upload to Cloudinary via storage backend
            with open(path, 'rb') as f:
                fname = os.path.basename(path)
                print(f"→ Uploading {fname}...")
                # This will use your configured storage backend (Cloudinary)
                post.image.save(fname, File(f), save=True)
                # Force a DB refresh to get the new URL
                post.refresh_from_db()
                print(f"✓ Success! New URL: {post.image.url}")
                # Double check the URL is actually from Cloudinary
                if not 'cloudinary' in post.image.url:
                    print("  Warning: URL does not appear to be from Cloudinary!")
                count['success'] += 1

        except Exception as e:
            print(f"→ Error processing post: {e}")
            count['error'] += 1
            continue

    # Print summary
    print("\nMigration Complete!")
    print(f"Successfully migrated: {count['success']}")
    print(f"Already remote (skipped): {count['skipped']}")
    print(f"Errors: {count['error']}")

if __name__ == '__main__':
    # Verify Cloudinary settings
    try:
        from django.conf import settings
        cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
        api_key = settings.CLOUDINARY_STORAGE.get('API_KEY')
        if not cloud_name or not api_key:
            print("Error: Cloudinary settings not configured properly!")
            print("Make sure CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY are set.")
            sys.exit(1)
    except Exception as e:
        print(f"Error checking Cloudinary settings: {e}")
        sys.exit(1)

    # Run migration
    migrate_images()