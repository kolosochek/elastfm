import os
import django
import elastfm.settings

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elastfm.settings')

application = get_wsgi_application()
