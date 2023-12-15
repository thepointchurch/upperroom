# pylint: disable=no-member

from django.conf import settings as django_settings
from storages.backends.s3boto3 import S3Boto3Storage  # pylint: disable=import-error

_STATIC_CUSTOM_DOMAIN = None
if "." in django_settings.STATICFILES_BUCKET:
    _STATIC_CUSTOM_DOMAIN = django_settings.STATICFILES_BUCKET

_MEDIA_CUSTOM_DOMAIN = None
if "." in django_settings.MEDIAFILES_BUCKET:
    _MEDIA_CUSTOM_DOMAIN = django_settings.MEDIAFILES_BUCKET


class S3StaticStorage(S3Boto3Storage):  # pylint: disable=abstract-method,too-few-public-methods
    def get_default_settings(self):
        defaults = super().get_default_settings()
        defaults["bucket_name"] = django_settings.STATICFILES_BUCKET
        defaults["querystring_auth"] = False
        defaults["secure_urls"] = False
        defaults["url_protocol"] = ""
        defaults["use_dualstack_endpoint"] = True
        defaults["custom_domain"] = _STATIC_CUSTOM_DOMAIN
        return defaults


class S3Boto3StorageOffload(S3Boto3Storage):  # pylint: disable=abstract-method,too-few-public-methods
    try:
        offload = django_settings.MEDIAFILES_OFFLOAD
    except (AttributeError, NameError):
        offload = False


class S3MediaStorage(S3Boto3StorageOffload):  # pylint: disable=abstract-method
    def __init__(self, **settings):
        super().__init__(**settings)
        self._unencrypted_keys = set()
        self._encrypted = django_settings.MEDIAFILES_ENCRYPTED

    def get_default_settings(self):
        defaults = super().get_default_settings()
        defaults["bucket_name"] = django_settings.MEDIAFILES_BUCKET
        defaults["querystring_auth"] = True
        defaults["querystring_expire"] = 300
        defaults["default_acl"] = "private"
        defaults["secure_urls"] = False
        defaults["url_protocol"] = ""
        defaults["use_dualstack_endpoint"] = True
        defaults["custom_domain"] = _MEDIA_CUSTOM_DOMAIN
        return defaults

    def get_object_parameters(self, name):
        params = super().get_object_parameters(name)
        if self._encrypted and name not in self._unencrypted_keys:
            params["ServerSideEncryption"] = "aws:kms"
        return params

    def save_cleartext(self, name):
        self._unencrypted_keys.add(name)

    def _save(self, name, content):
        clean_name = super()._save(name, content)
        self._unencrypted_keys.discard(name)
        return clean_name
