#!/usr/bin/env python
import os
import sys
import cloudinary
import cloudinary.uploader
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'embracingmain.settings')
django.setup()

from main.models import Post
from django.core.files import File
from django.conf import settings

def migrate_images():
    print("Starting media migration to Cloudinary...")
    count = {'success': 0, 'skipped': 0, 'error': 0}
    
    # Get all posts with images
    posts = Post.objects.filter(image__isnull=False)
    total = posts.count()
    print(f"Found {total} posts with images")
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_STORAGE['CLOUD_NAME'],
        api_key=settings.CLOUDINARY_STORAGE['API_KEY'],
        api_secret=settings.CLOUDINARY_STORAGE['API_SECRET']
    )
    
    for i, post in enumerate(posts, 1):
        print(f"\nProcessing {i}/{total}: {post.title}")
        try:
            # If URL is already a cloudinary URL, skip it
            url = getattr(post.image, 'url', '')
            if 'cloudinary' in url:
                print(f"→ Skipping (already on Cloudinary): {url}")
                count['skipped'] += 1
                continue

            # Get original file name without any suffixes
            url = str(post.image)
            fname = os.path.basename(url).split('_')[0]  # Remove any _XYZ suffixes
            if not '.' in fname:  # If we accidentally removed the extension
                fname = os.path.basename(url)  # Use full name
            
            # Look in static/media directory
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'static', 'media', 'post_images', fname)
            
            if not os.path.exists(path):
                print(f"→ Error: File not found at: {path}")
                count['error'] += 1
                continue

            print(f"→ Uploading {fname} to Cloudinary...")
            
            # Upload directly to Cloudinary
            with open(path, 'rb') as f:
                # Upload to Cloudinary with specific folder and type
                result = cloudinary.uploader.upload(
                    f,
                    folder="embracinggirlchild/blog_images",
                    public_id=os.path.splitext(fname)[0],
                    overwrite=True,
                    resource_type="auto"
                )
                
                # Update the post with the new Cloudinary URL
                cloudinary_url = result['secure_url']
                post.image = cloudinary_url
                post.save()
                
                print(f"✓ Success! New URL: {cloudinary_url}")
                count['success'] += 1

        except Exception as e:
            print(f"→ Error processing post: {e}")
            count['error'] += 1
            continue

    # Print summary
    print("\nMigration Complete!")
    print(f"Successfully migrated: {count['success']}")
    print(f"Already on Cloudinary: {count['skipped']}")
    print(f"Errors: {count['error']}")

if __name__ == '__main__':
    migrate_images()