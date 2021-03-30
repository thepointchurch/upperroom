from pathlib import Path

from upperroom.settings import *  # NOQA: F403 pylint: disable=wildcard-import,unused-wildcard-import

BASE_DIR = Path(__file__).resolve(strict=True).parent
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]  # NOQA: F405
STATICFILES_DIRS = (BASE_DIR / "static",)

ROOT_URLCONF = "thepoint.urls"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Australia/Brisbane"

WEBMASTER_EMAIL = "webmaster@thepoint.org.au"
DIRECTORY_EMAIL = "directory@thepoint.org.au"
ROSTER_EMAIL = "roster@thepoint.org.au"
DEFAULT_FROM_EMAIL = WEBMASTER_EMAIL
