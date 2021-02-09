# pylint: disable=no-member

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage  # pylint: disable=import-error

_STATIC_CUSTOM_DOMAIN = None
if "." in settings.STATICFILES_BUCKET:
    _STATIC_CUSTOM_DOMAIN = settings.STATICFILES_BUCKET

_MEDIA_CUSTOM_DOMAIN = None
if "." in settings.MEDIAFILES_BUCKET:
    _MEDIA_CUSTOM_DOMAIN = settings.MEDIAFILES_BUCKET


class S3StaticStorage(S3Boto3Storage):  # pylint: disable=abstract-method,too-few-public-methods
    def get_default_settings(self):
        defaults = super().get_default_settings()
        defaults["bucket_name"] = settings.STATICFILES_BUCKET
        defaults["querystring_auth"] = False
        defaults["secure_urls"] = False
        defaults["url_protocol"] = ""
        defaults["custom_domain"] = _STATIC_CUSTOM_DOMAIN
        return defaults


class S3Boto3StorageOffload(S3Boto3Storage):  # pylint: disable=abstract-method,too-few-public-methods
    try:
        offload = settings.MEDIAFILES_OFFLOAD
    except (AttributeError, NameError):
        offload = False


class S3MediaStorage(S3Boto3StorageOffload):  # pylint: disable=abstract-method
    def get_default_settings(self):
        defaults = super().get_default_settings()
        defaults["bucket_name"] = settings.MEDIAFILES_BUCKET
        defaults["querystring_auth"] = True
        defaults["querystring_expire"] = 300
        defaults["default_acl"] = "private"
        defaults["secure_urls"] = False
        defaults["url_protocol"] = ""
        defaults["custom_domain"] = _MEDIA_CUSTOM_DOMAIN
        return defaults
