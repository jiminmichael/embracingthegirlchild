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
    
    for i, post in enumerate(posts, 1):
        print(f"\nProcessing {i}/{total}: {post.title}")
        try:
            # Get the image file path from the database value
            image_name = str(post.image)  # This will be like 'post_images/filename.jpg'
            if not image_name:
                print("→ No image field value")
                count['error'] += 1
                continue
                
            # Strip off the upload_to prefix if present
            if '/' in image_name:
                image_name = image_name.split('/')[-1]
            
            # Look in static/media directory
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              'static', 'media', 'post_images', image_name)
            
            if not os.path.exists(path):
                print(f"→ Error: File not found at: {path}")
                count['error'] += 1
                continue
            
            print(f"→ Uploading {image_name} to Cloudinary...")
            
            # Upload to Cloudinary directly
            with open(path, 'rb') as f:
                result = cloudinary.uploader.upload(
                    f,
                    folder="embracinggirlchild/blog_images",
                    public_id=os.path.splitext(image_name)[0],
                    overwrite=True,
                    resource_type="auto"
                )
                
                # Update the post's image field to the Cloudinary URL
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
    # Verify Cloudinary environment variables
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
    api_key = os.environ.get('CLOUDINARY_API_KEY')
    api_secret = os.environ.get('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        print("Error: Cloudinary environment variables not set!")
        print("Make sure to set:")
        print("- CLOUDINARY_CLOUD_NAME")
        print("- CLOUDINARY_API_KEY")
        print("- CLOUDINARY_API_SECRET")
        sys.exit(1)
        
    # Initialize Cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret
    )
    
    # Run migration
    migrate_images()