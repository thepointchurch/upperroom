from pathlib import Path

import environ

env = environ.Env(
    AWS_DEFAULT_REGION=(str, None),
    CACHE_TIMEOUT=(int, 300),
    CACHE_URL=(str, "dummycache://"),
    CACHEOPS_ENABLED=(bool, False),
    DEBUG=(bool, False),
    DEBUG_TOOLBAR=(bool, False),
    EMAIL_URL=(str, "consolemail://"),
    EMAIL_BACKEND=(str, None),
    MEDIAFILES_BUCKET=(str, None),
    MEDIAFILES_ENCRYPTED=(bool, False),
    SITE_ID=(int, 1),
    STATIC_URL=(str, "/static/"),
    STATICFILES_BUCKET=(str, None),
    VHOST=(str, "*"),
)
environ.Env.read_env(".env")


BASE_DIR = Path(__file__).resolve(strict=True).parent

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

EMAIL_BACKEND = env.email(backend=env("EMAIL_BACKEND"))["EMAIL_BACKEND"]

ALLOWED_HOSTS = env("VHOST").split()

SITE_ID = env("SITE_ID")

CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE", default=(not DEBUG))
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE", default=(not DEBUG))
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

INSTALLED_APPS = [
    "upperroom.directory.apps.DirectoryConfig",
    "upperroom.extendedsites.apps.ExtendedSitesConfig",
    "upperroom.library.apps.LibraryConfig",
    "upperroom.members.apps.MembersConfig",
    "upperroom.newsletter.apps.NewsletterConfig",
    "upperroom.resources.apps.ResourcesConfig",
    "upperroom.weblog.apps.WeblogConfig",
    "robots",
    "upperroom.roster.apps.RosterConfig",
    "upperroom.search.apps.SearchConfig",
    "upperroom.splash.apps.SplashConfig",
    "upperroom.utils.apps.UtilsConfig",
    "django_markwhat",
    "django.contrib.admin.apps.AdminConfig",
    "django.contrib.auth.apps.AuthConfig",
    "django.contrib.contenttypes.apps.ContentTypesConfig",
    "django.contrib.flatpages.apps.FlatPagesConfig",
    "django.contrib.redirects.apps.RedirectsConfig",
    "django.contrib.sessions.apps.SessionsConfig",
    "django.contrib.sites.apps.SitesConfig",
    "django.contrib.messages.apps.MessagesConfig",
    "django.contrib.sitemaps.apps.SiteMapsConfig",
    "django.contrib.staticfiles.apps.StaticFilesConfig",
]

MIDDLEWARE = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
    "upperroom.members.middleware.UsernameHeaderMiddleware",
    "upperroom.resources.middleware.ResourceFallbackMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]

ROOT_URLCONF = "upperroom.urls"
WSGI_APPLICATION = "upperroom.wsgi.application"

DATABASES = {
    "default": env.db(),
}

USE_I18N = True
USE_L10N = True
USE_TZ = True

WEBMASTER_EMAIL = None

LOGIN_URL = "/members/login"
LOGIN_REDIRECT_URL = "/members/"

DATA_ROOT = Path(".") / "data"

MEDIA_ROOT = DATA_ROOT / "media"

STATIC_URL = env("STATIC_URL")
STATIC_ROOT = DATA_ROOT / "static"
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
STATICFILES_DIRS = (BASE_DIR / "static",)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "upperroom.extendedsites.context_processors.site",
                "upperroom.resources.context_processors.featured_tags",
                "upperroom.splash.context_processors.splashes",
            ],
        },
    },
]

FORM_RENDERER = "django.forms.renderers.DjangoDivFormRenderer"

PASSWORD_HASHERS = (
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
)

ROBOTS_CACHE_TIMEOUT = 60 * 60 * 24


CACHES = {
    "default": env.cache(),
}
CACHES["default"]["TIMEOUT"] = env("CACHE_TIMEOUT")

if "dummy" not in CACHES["default"]["BACKEND"]:
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

CACHEOPS_DEFAULTS = {
    "timeout": CACHES["default"].get("TIMEOUT", 60 * 60 * 24),
}

CACHEOPS = {
    "auth.user": {"ops": "get", "timeout": 60 * 15},
    "auth.*": {"ops": ("fetch", "get")},
    "auth.permission": {"ops": "all"},
    "directory.*": {"ops": "all"},
    "extendedsites.*": {"ops": "all"},
    "library.*": {"ops": "all"},
    "newsletter.*": {"ops": "all"},
    "resources.*": {"ops": "all"},
    "roster.*": {"ops": "all"},
    "splash.*": {"ops": "all"},
    "weblog.*": {"ops": "all"},
    "flatpages.*": {"ops": "all"},
    "redirects.*": {"ops": "all"},
    "robots.*": {"ops": "all"},
    "sites.*": {"ops": "all"},
}

if "redis" in CACHES["default"].get("LOCATION", ""):
    CACHEOPS_REDIS = CACHES["default"]["LOCATION"]
    CACHEOPS_ENABLED = env("CACHEOPS_ENABLED")
else:
    CACHEOPS_ENABLED = False
if CACHEOPS_ENABLED:
    INSTALLED_APPS.append("cacheops")
CACHEOPS_DEGRADE_ON_FAILURE = True
DJANGO_REDIS_IGNORE_EXCEPTIONS = True
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

CACHE_MIDDLEWARE_ALIAS = "default"
CACHE_MIDDLEWARE_KEY_PREFIX = ""


CSP_DEFAULT_SRC = ("'self'",)
CSP_IMG_SRC = ("'self'", "data:")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "fonts.gstatic.com")
CSP_SCRIPT_SRC = ("'self'", "cdnjs.cloudflare.com")
CSP_OBJECT_SRC = ("'none'",)


if env("STATICFILES_BUCKET") or env("MEDIAFILES_BUCKET"):
    INSTALLED_APPS += ("storages",)

    STATICFILES_BUCKET = env("STATICFILES_BUCKET")
    STATICFILES_STORAGE = "upperroom.utils.storages.backends.S3StaticStorage"
    if STATICFILES_BUCKET:
        CSP_IMG_SRC += (STATICFILES_BUCKET,)
        CSP_STYLE_SRC += (STATICFILES_BUCKET,)
        CSP_FONT_SRC += (STATICFILES_BUCKET,)
        CSP_SCRIPT_SRC += (STATICFILES_BUCKET,)

    MEDIAFILES_OFFLOAD = True
    MEDIAFILES_ENCRYPTED = env("MEDIAFILES_ENCRYPTED")
    MEDIAFILES_BUCKET = env("MEDIAFILES_BUCKET")
    DEFAULT_FILE_STORAGE = "upperroom.utils.storages.backends.S3MediaStorage"
    if MEDIAFILES_BUCKET:
        if "." not in MEDIAFILES_BUCKET:
            CSP_IMG_SRC += (MEDIAFILES_BUCKET + ".s3.amazonaws.com",)
        else:
            CSP_IMG_SRC += (MEDIAFILES_BUCKET,)

    AWS_DEFAULT_ACL = None

    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }

    AWS_S3_SIGNATURE_VERSION = "s3v4"


AWS_DEFAULT_REGION = env("AWS_DEFAULT_REGION")


if DEBUG and env("DEBUG_TOOLBAR"):
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]
    DEBUG_TOOLBAR = True
else:
    DEBUG_TOOLBAR = False


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}},
    "handlers": {
        "default": {"class": "logging.StreamHandler", "formatter": "standard"},
        "null": {"class": "logging.NullHandler"},
    },
    "loggers": {
        "django": {"handlers": ["default"], "level": "DEBUG" if DEBUG else "INFO", "propagate": False},
        "django.db": {"handlers": ["null"], "propagate": False},
    },
}
