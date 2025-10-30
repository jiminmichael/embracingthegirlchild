import os
import sys
import django
import cloudinary
import cloudinary.uploader

# Set up Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'embracingmain.settings')

# Set Cloudinary environment variables
os.environ['CLOUDINARY_CLOUD_NAME'] = 'djogcbblz'
os.environ['CLOUDINARY_API_KEY'] = '837879196287172'
os.environ['CLOUDINARY_API_SECRET'] = 'ZmpPKNskxpVm5hHte8FskOxMrGM'

django.setup()

from main.models import Post
from django.core.files import File

def find_image(image_name):
    """Try to find the image in various possible locations"""
    possible_paths = [
        os.path.join('static', 'media', str(image_name)),
        os.path.join('static', 'media', 'post_images', os.path.basename(str(image_name))),
        os.path.join('staticfiles', 'media', str(image_name)),
        os.path.join('staticfiles', 'media', 'post_images', os.path.basename(str(image_name))),
        os.path.join('media', str(image_name)),
        os.path.join('media', 'post_images', os.path.basename(str(image_name))),
        os.path.join('staticfiles', 'images', os.path.basename(str(image_name))),
        os.path.join('static', 'images', os.path.basename(str(image_name))),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def upload_images():
    print("Starting image upload to Cloudinary...")
    posts = Post.objects.filter(image__isnull=False)
    
    print("\nLooking for images in these directories:")
    print("Current directory:", os.getcwd())
    print("Contents of static/:")
    try:
        print(os.listdir('static'))
    except:
        print("(not found)")
    print("\nContents of staticfiles/:")
    try:
        print(os.listdir('staticfiles'))
    except:
        print("(not found)")
    
    for post in posts:
        if not post.image:
            continue
            
        print(f"\nProcessing: {post.title}")
        print(f"Looking for image: {post.image}")
        
        # Try to find the image
        local_path = find_image(post.image)
        if not local_path:
            print(f"❌ Image not found in any expected location")
            continue
            
        print(f"Found at: {local_path}")
        
        try:
            # Upload to Cloudinary
            with open(local_path, 'rb') as image_file:
                result = cloudinary.uploader.upload(
                    image_file,
                    folder=f"embracingthegirlchild/post_images",
                    public_id=os.path.splitext(os.path.basename(str(post.image)))[0],
                    use_filename=True,
                    unique_filename=False,
                    overwrite=True
                )
                print(f"✓ Uploaded successfully")
                print(f"Cloudinary URL: {result['secure_url']}")
                
        except Exception as e:
            print(f"❌ Error uploading: {str(e)}")
            continue

if __name__ == '__main__':
    upload_images()