#!/usr/bin/env python
import os
import sys
import cloudinary
import cloudinary.uploader
import django
import re

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'embracingmain.settings')
django.setup()

from main.models import Post
from django.core.files import File
from django.conf import settings

def find_original_image(filename):
    """Find the original image file by removing any random suffixes Django added."""
    # Get base name without extension
    base, ext = os.path.splitext(filename)
    
    # Remove random suffix if present (_XXXXX)
    base = re.sub(r'_[a-zA-Z0-9]+$', '', base)
    
    # Path to static/media/post_images directory
    media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                          'static', 'media', 'post_images')
    
    # Try exact match first
    exact_path = os.path.join(media_dir, base + ext)
    if os.path.exists(exact_path):
        return exact_path
        
    # List all files in the directory
    try:
        files = os.listdir(media_dir)
    except OSError:
        print(f"Warning: Could not read directory {media_dir}")
        return None
        
    # Try to find a match ignoring any random suffixes
    pattern = re.compile(re.escape(base) + r'(?:_[a-zA-Z0-9]+)?' + re.escape(ext))
    matches = [f for f in files if pattern.match(f)]
    
    if matches:
        return os.path.join(media_dir, matches[0])
    
    return None

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
            
            # Try to find the original image file
            image_path = find_original_image(image_name)
            if not image_path:
                print(f"→ Error: Could not find original image for {image_name}")
                count['error'] += 1
                continue
            
            print(f"→ Found original image at: {image_path}")
            print(f"→ Uploading to Cloudinary...")
            
            # Upload to Cloudinary directly
            with open(image_path, 'rb') as f:
                result = cloudinary.uploader.upload(
                    f,
                    folder="embracinggirlchild/blog_images",
                    public_id=os.path.splitext(os.path.basename(image_path))[0],
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