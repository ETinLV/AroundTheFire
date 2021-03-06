from .settings import *

# Override debug setting and 'SECRET KEY'
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']

# Allows apps in blacklist to not be installed
BLACKLIST = []
INSTALLED_APPS = tuple([app for app in INSTALLED_APPS if app not in BLACKLIST])

# Parse database configuration from $DATABASE_URL
import dj_database_url

DATABASES['default'] = dj_database_url.config()

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Static asset configuration
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'static'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, '../global/'),
)
