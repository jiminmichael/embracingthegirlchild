from django import template
from django.conf import settings
from django.templatetags.static import static
from cloudinary_storage.storage import MediaCloudinaryStorage

register = template.Library()

@register.filter
def gallery_image_url(image_path):
    """
    Template filter to handle both static and media images.
    Usage: {{ 'path/to/image.jpg'|gallery_image_url }}
    """
    if not image_path:
        return ''
        
    # If it starts with 'media/post_images/', treat as a Cloudinary image
    if image_path.startswith('media/post_images/'):
        storage = MediaCloudinaryStorage()
        return storage.url(image_path.replace('media/', '', 1))
        
    # Otherwise treat as static
    return static(image_path)