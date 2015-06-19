import logging
import os
import sys

sys.path.append('apps')

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = bool(os.getenv('DEBUG', False))
TEMPLATE_DEBUG = bool(os.getenv('DEBUG', False))

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND',
                          'django.core.mail.backends.console.EmailBackend')

ALLOWED_HOSTS = os.getenv('VHOST', '*').split()

SITE_ID = int(os.getenv('SITE_ID', 1))


INSTALLED_APPS = (
    'directory',
    'library',
    'members',
    'newsletter',
    'pages',
    'resources',
    'roster',
    'django_markwhat',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.flatpages',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'thepoint.urls'
WSGI_APPLICATION = 'thepoint.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.environ['DB_ENGINE'],
        'NAME': os.environ['DB_NAME'],
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Brisbane'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOGIN_URL = '/members/login'
LOGIN_REDIRECT_URL = '/members/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'thepoint/static'),
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'thepoint/templates'),
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
)


class AddEnvironmentFilter(logging.Filter):
    def __init__(self, environment):
        self.environment = environment

    def filter(self, record):
        record.environment = self.environment
        return True


if os.getenv('environment', '') in ['production', 'testing']:
    if DEBUG:
        level = 'DEBUG'
    else:
        level = 'INFO'

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'filters': {
            'add_environment': {
                '()': AddEnvironmentFilter,
                'environment': os.getenv('environment', ''),
            },
        },
        'formatters': {
            'syslog': {
                'format': ('django_%(environment)s[%(process)d]: '
                           '%(name)s [%(levelname)s] %(message)s')
            },
        },
        'handlers': {
            'syslog': {
                'level': level,
                'class': 'logging.handlers.SysLogHandler',
                'address': '/dev/log',
                'formatter': 'syslog',
                'filters': ['add_environment'],
            },
        },
        'loggers': {
            'root': {
                'handlers': ['syslog'],
                'level': level,
            },
            'django': {
                'handlers': ['syslog'],
                'level': level,
                'propagate': False,
            },
            'django.request': {
                'handlers': ['syslog'],
                'level': level,
                'propagate': False,
            },
            'django.security': {
                'handlers': ['syslog'],
                'level': level,
                'propagate': False,
            },
            'gunicorn.access': {
                'handlers': ['syslog'],
                'level': level,
                'propagate': False,
            },
            'gunicorn.error': {
                'handlers': ['syslog'],
                'level': level,
                'propagate': False,
            },
            'py.warnings': {
                'handlers': ['syslog'],
                'level': level,
                'propagate': False,
            },
        }
    }

    INSTALLED_APPS += ('storages',)

    STATICFILES_BUCKET = os.getenv('STATICFILES_BUCKET',
                                   'static.%s' % ALLOWED_HOSTS[0])
    STATICFILES_STORAGE = 'util.storages.backends.S3StaticStorage'

    MEDIAFILES_OFFLOAD = True
    MEDIAFILES_BUCKET = os.getenv('MEDIAFILES_BUCKET',
                                  'media.%s' % ALLOWED_HOSTS[0])
    DEFAULT_FILE_STORAGE = 'util.storages.backends.S3MediaStorage'

else:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
            'null': {
                'level': 'DEBUG',
                'class': 'logging.NullHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'DEBUG',
            },
            'django.db': {
                'handlers': ['null'],
                'level': 'DEBUG',
                'propagate': False,
            },
        }
    }
