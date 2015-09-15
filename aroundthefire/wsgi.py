import os
from dj_static import Cling
from django.core.wsgi import get_wsgi_application

# Set the environment variables
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aroundthefire.settings")

application = Cling(get_wsgi_application())
