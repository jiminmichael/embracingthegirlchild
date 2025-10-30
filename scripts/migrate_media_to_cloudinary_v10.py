#!/usr/bin/env python
import os
import sys
import django
import re
import cloudinary
import cloudinary.uploader

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'embracingmain.settings')
django.setup()

from django.core.files import File
from main.models import Post

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
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=os.environ['CLOUDINARY_CLOUD_NAME'],
        api_key=os.environ['CLOUDINARY_API_KEY'],
        api_secret=os.environ['CLOUDINARY_API_SECRET']
    )
    
    for i, post in enumerate(posts, 1):
        print(f"\nProcessing {i}/{total}: {post.title}")
        try:
            # Get the image file path from the database value
            image_name = str(post.image)  # This will be like 'post_images/filename.jpg'
            if not image_name:
                print("→ No image field value")
                count['error'] += 1
                continue
                
            # If it's already a Cloudinary URL, skip it
            if 'cloudinary' in image_name:
                print(f"→ Already on Cloudinary: {image_name}")
                count['skipped'] += 1
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
            
            # Upload to Cloudinary
            with open(image_path, 'rb') as f:
                file_name = os.path.basename(image_path)
                base_name, ext = os.path.splitext(file_name)
                
                # Upload directly to Cloudinary
                result = cloudinary.uploader.upload(image_path,
                    folder="blog_images",
                    public_id=base_name,
                    overwrite=True)
                
                # Get the secure URL
                cloudinary_url = result['secure_url']
                print(f"→ Cloudinary upload successful, URL: {cloudinary_url}")
                
                # Update the post
                post.image = cloudinary_url
                post.save()
                
                print(f"✓ Success! Updated post with new URL")
                count['success'] += 1

        except Exception as e:
            print(f"→ Error processing post: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            count['error'] += 1
            continue

    # Print summary
    print("\nMigration Complete!")
    print(f"Successfully migrated: {count['success']}")
    print(f"Already on Cloudinary: {count['skipped']}")
    print(f"Errors: {count['error']}")

if __name__ == '__main__':
    # Run migration
    migrate_images()