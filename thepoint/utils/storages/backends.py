# pylint: disable=no-member

from urllib.parse import urlsplit

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage  # pylint: disable=import-error

_STATIC_CUSTOM_DOMAIN = None
if "." in settings.STATICFILES_BUCKET:
    _static_custom_domain = settings.STATICFILES_BUCKET

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

    def url(self, name, parameters=None, expire=None, http_method=None):
        _, _ = expire, http_method
        # Generate the S3 offload URL but enforce our protocol and domain
        name = self._normalize_name(self._clean_name(name))
        params = parameters.copy() if parameters else {}
        params["Bucket"] = self.bucket.name
        params["Key"] = name
        url = self.bucket.meta.client.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=self.querystring_expire
        )
        url = urlsplit(url)
        if self.custom_domain:
            domain = self.custom_domain
            url_path = "/".join(x for x in url.path.split("/") if x != self.custom_domain)
        else:
            domain = url.netloc
            url_path = url.path
        return "%s//%s%s?%s" % (self.url_protocol, domain, url_path, url.query)


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
