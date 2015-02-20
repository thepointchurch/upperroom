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
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

MIDDLEWARE_CLASSES = (
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

if os.getenv('environment', '') in ['production', 'testing']:
    if DEBUG:
        level = 'DEBUG'
    else:
        level = 'INFO'

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'cloudwatch': {
                'format': '[%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': level,
                'class': 'util.logging.handlers.CloudwatchHandler',
                'group': '%s_%s' % (os.uname()[1], ALLOWED_HOSTS[0]),
                'stream': 'django',
                'formatter': 'cloudwatch',
            },
            'request': {
                'level': level,
                'class': 'util.logging.handlers.CloudwatchHandler',
                'group': '%s_%s' % (os.uname()[1], ALLOWED_HOSTS[0]),
                'stream': 'request',
                'formatter': 'cloudwatch',
            },
            'security': {
                'level': level,
                'class': 'util.logging.handlers.CloudwatchHandler',
                'group': '%s_%s' % (os.uname()[1], ALLOWED_HOSTS[0]),
                'stream': 'security',
                'formatter': 'cloudwatch',
            },
            'gunicorn': {
                'level': level,
                'class': 'util.logging.handlers.CloudwatchHandler',
                'group': '%s_%s' % (os.uname()[1], ALLOWED_HOSTS[0]),
                'stream': 'gunicorn',
                'formatter': 'cloudwatch',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': level,
            },
            'django.request': {
                'handlers': ['request'],
                'level': level,
                'propagate': False,
            },
            'django.security': {
                'handlers': ['security'],
                'level': level,
                'propagate': False,
            },
            'gunicorn.error': {
                'handlers': ['gunicorn'],
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
