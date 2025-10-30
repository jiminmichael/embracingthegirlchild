#!/usr/bin/env python
import os
import sys
import django
from django.core.files import File

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'embracingmain.settings')
django.setup()

from main.models import Post
from django.contrib.auth.models import User

def create_test_post():
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='jimin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    
    # Create a test post
    post = Post.objects.create(
        title='Test Post with Image',
        content='This is a test post to verify image upload functionality.',
        author=user
    )
    
    # Add image
    image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                             'static', 'media', 'post_images', 'amaka.jpg')
    
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            post.image.save('amaka.jpg', File(f), save=True)
        print(f"Successfully created test post with image: {post.image.url}")
    else:
        print(f"Could not find image file at: {image_path}")

    print("Post ID:", post.id)
    print("Title:", post.title)
    print("Image field:", post.image)
    try:
        print("Image URL:", post.image.url)
    except Exception as e:
        print("Error getting image URL:", e)

if __name__ == '__main__':
    create_test_post()