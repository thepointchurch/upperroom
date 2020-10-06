import os

from django.core.wsgi import get_wsgi_application

from .commands import import_file_env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thepoint.settings")

import_file_env()

application = get_wsgi_application()
