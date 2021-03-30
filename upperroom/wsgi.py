from django.core.wsgi import get_wsgi_application

from .commands import import_file_env

import_file_env()

application = get_wsgi_application()
