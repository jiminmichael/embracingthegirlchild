"""Production Settings for Render"""
import os
import dj_database_url
from .settings import *

# Set DEBUG to False
DEBUG = False

# Add Render URL to ALLOWED_HOSTS
ALLOWED_HOSTS.extend(
    ['embracingthegirlchild.onrender.com', '.onrender.com', 'localhost', '127.0.0.1']
)

# Configure database using DATABASE_URL environment variable
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Configure static file storage
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add whitenoise middleware
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Configure media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True