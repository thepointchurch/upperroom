import logging
import os

BASE_DIR = os.path.dirname(__file__)

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = bool(os.getenv('DEBUG', False))

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND',
                          'django.core.mail.backends.console.EmailBackend')

ALLOWED_HOSTS = os.getenv('VHOST', '*').split()

SITE_ID = int(os.getenv('SITE_ID', 1))


INSTALLED_APPS = (
    'thepoint.apps.directory.apps.DirectoryConfig',
    'thepoint.apps.library.apps.LibraryConfig',
    'thepoint.apps.members.apps.MembersConfig',
    'thepoint.apps.newsletter.apps.NewsletterConfig',
    'thepoint.apps.pages.apps.PagesConfig',
    'thepoint.apps.resources.apps.ResourcesConfig',
    'robots',
    'thepoint.apps.roster.apps.RosterConfig',
    'thepoint.apps.splash.apps.SplashConfig',
    'django_markwhat',
    'django.contrib.admin.apps.AdminConfig',
    'django.contrib.auth.apps.AuthConfig',
    'django.contrib.contenttypes.apps.ContentTypesConfig',
    'django.contrib.flatpages.apps.FlatPagesConfig',
    'django.contrib.redirects.apps.RedirectsConfig',
    'django.contrib.sessions.apps.SessionsConfig',
    'django.contrib.sites.apps.SitesConfig',
    'django.contrib.messages.apps.MessagesConfig',
    'django.contrib.sitemaps.apps.SiteMapsConfig',
    'django.contrib.staticfiles.apps.StaticFilesConfig',
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
    'thepoint.apps.resources.middleware.ResourceFallbackMiddleware',
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

SITE_NAME = 'The Point'

DEFAULT_FROM_EMAIL = 'webmaster@thepoint.org.au'
DIRECTORY_NOTIFY_EMAIL = 'directory@thepoint.org.au'

LOGIN_URL = '/members/login'
LOGIN_REDIRECT_URL = '/members/'

MEDIA_ROOT = os.path.join('.', 'media')

STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = os.path.join('.', 'static')
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'thepoint.apps.resources.context_processors.featured_tags',
                'thepoint.apps.splash.context_processors.splashes',
            ],
        },
    },
]

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
)

ROBOTS_CACHE_TIMEOUT = 60*60*24


if os.getenv('STATICFILES_BUCKET', None) or os.getenv('MEDIAFILES_BUCKET', None):
    INSTALLED_APPS += ('storages',)

    STATICFILES_BUCKET = os.getenv('STATICFILES_BUCKET',
                                   'static.%s' % ALLOWED_HOSTS[0])
    STATICFILES_STORAGE = 'thepoint.util.storages.backends.S3StaticStorage'

    MEDIAFILES_OFFLOAD = True
    MEDIAFILES_BUCKET = os.getenv('MEDIAFILES_BUCKET',
                                  'media.%s' % ALLOWED_HOSTS[0])
    DEFAULT_FILE_STORAGE = 'thepoint.util.storages.backends.S3MediaStorage'


class AddSyslogTagFilter(logging.Filter):
    def __init__(self, tag):
        self.tag = tag

    def filter(self, record):
        record.tag = self.tag
        return True


if os.getenv('SYSLOG_TAG', ''):
    if DEBUG:
        level = 'DEBUG'
    else:
        level = 'INFO'

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'filters': {
            'add_syslog_tag': {
                '()': AddSyslogTagFilter,
                'tag': os.getenv('SYSLOG_TAG', ''),
            },
        },
        'formatters': {
            'syslog': {
                'format': ('django_%(tag)s[%(process)d]: '
                           '%(name)s [%(levelname)s] %(message)s')
            },
        },
        'handlers': {
            'syslog': {
                'level': level,
                'class': 'logging.handlers.SysLogHandler',
                'address': '/dev/log',
                'formatter': 'syslog',
                'filters': ['add_syslog_tag'],
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
