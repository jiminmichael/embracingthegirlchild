#!/usr/bin/env python
import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'embracingmain.settings')
django.setup()

from main.models import Post

def debug_images():
    # Check all posts, even those without images
    posts = Post.objects.all()
    print(f"Total posts: {posts.count()}")
    print("Checking all posts...\n")
    
    for post in posts:
        print(f"Post: {post.title}")
        print(f"Raw image field value: {getattr(post, 'image', None)}")
        try:
            print(f"Image field value: {post.image}")
            print(f"Image URL: {post.image.url}")
        except Exception as e:
            print(f"Error accessing image field: {e}")
        print("--------------------------------------------------")