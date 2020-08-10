import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent

SECRET_KEY = os.environ['SECRET_KEY']

DEBUG = bool(os.getenv('DEBUG', False))

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND',
                          'django.core.mail.backends.console.EmailBackend')

ALLOWED_HOSTS = os.getenv('VHOST', '*').split()

SITE_ID = int(os.getenv('SITE_ID', 1))


INSTALLED_APPS = (
    'thepoint.apps.directory.apps.DirectoryConfig',
    'thepoint.apps.extendedsites.apps.ExtendedSitesConfig',
    'thepoint.apps.library.apps.LibraryConfig',
    'thepoint.apps.members.apps.MembersConfig',
    'thepoint.apps.newsletter.apps.NewsletterConfig',
    'thepoint.apps.resources.apps.ResourcesConfig',
    'thepoint.apps.weblog.apps.WeblogConfig',
    'robots',
    'thepoint.apps.roster.apps.RosterConfig',
    'thepoint.apps.splash.apps.SplashConfig',
    'thepoint.apps.utils.apps.UtilsConfig',
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

MIDDLEWARE = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.redirects.middleware.RedirectFallbackMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'thepoint.apps.resources.middleware.ResourceFallbackMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'thepoint.urls'
WSGI_APPLICATION = 'thepoint.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.environ['DB_ENGINE'],
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Australia/Brisbane'
USE_I18N = True
USE_L10N = True
USE_TZ = True

WEBMASTER_EMAIL = 'webmaster@thepoint.org.au'
DIRECTORY_EMAIL = 'directory@thepoint.org.au'
ROSTER_EMAIL = 'roster@thepoint.org.au'

DEFAULT_FROM_EMAIL = WEBMASTER_EMAIL

LOGIN_URL = '/members/login'
LOGIN_REDIRECT_URL = '/members/'

MEDIA_ROOT = Path('.') / 'media'

STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = Path('.') / 'static'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
STATICFILES_DIRS = (
    BASE_DIR / 'static',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'thepoint.apps.extendedsites.context_processors.site',
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


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
for cache_var in ('BACKEND',
                  'KEY_FUNCTION',
                  'KEY_PREFIX',
                  'LOCATION',
                  'OPTIONS',
                  'TIMEOUT',
                  'VERSION',
                  ):
    value = os.getenv('CACHE_%s' % cache_var, None)
    if value:
        if cache_var == 'LOCATION' and value.count(' ') > 0:
            value = value.split(' ')
        if cache_var == 'TIMEOUT':
            value = int(value)
            CACHE_MIDDLEWARE_SECONDS = value
        if cache_var == 'OPTIONS':
            import json
            value = json.loads(value)
        CACHES['default'][cache_var] = value

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_KEY_PREFIX = ''


if os.getenv('STATICFILES_BUCKET', None) or os.getenv('MEDIAFILES_BUCKET', None):
    INSTALLED_APPS += ('storages',)

    STATICFILES_BUCKET = os.getenv('STATICFILES_BUCKET',
                                   'static.%s' % ALLOWED_HOSTS[0])
    STATICFILES_STORAGE = 'thepoint.apps.utils.storages.backends.S3StaticStorage'

    MEDIAFILES_OFFLOAD = True
    MEDIAFILES_BUCKET = os.getenv('MEDIAFILES_BUCKET',
                                  'media.%s' % ALLOWED_HOSTS[0])
    DEFAULT_FILE_STORAGE = 'thepoint.apps.utils.storages.backends.S3MediaStorage'

    AWS_DEFAULT_ACL = None

    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }


if os.getenv('AWS_DEFAULT_REGION', None):
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')


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
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['default'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
        'django.db': {
            'handlers': ['null'],
            'propagate': False,
        },
    }
}
