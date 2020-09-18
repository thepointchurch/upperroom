from urllib.parse import urlsplit

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

_STATIC_CUSTOM_DOMAIN = None
if "." in settings.STATICFILES_BUCKET:
    _static_custom_domain = settings.STATICFILES_BUCKET

S3StaticStorage = lambda: S3Boto3Storage(  # NOQA: E731
    bucket_name=settings.STATICFILES_BUCKET,
    querystring_auth=False,
    secure_urls=False,
    url_protocol="",
    custom_domain=_STATIC_CUSTOM_DOMAIN,
)


class S3Boto3StorageOffload(S3Boto3Storage):  # pylint: disable=abstract-method
    try:
        offload = settings.MEDIAFILES_OFFLOAD
    except (AttributeError, NameError):
        offload = False

    def url(self, name, parameters=None, expire=None):
        # Generate the S3 offload URL but enforce our protocol and domain
        name = self._normalize_name(self._clean_name(name))
        params = parameters.copy() if parameters else {}
        params["Bucket"] = self.bucket.name
        params["Key"] = self._encode_name(name)
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


_MEDIA_CUSTOM_DOMAIN = None
if "." in settings.MEDIAFILES_BUCKET:
    _MEDIA_CUSTOM_DOMAIN = settings.MEDIAFILES_BUCKET

S3MediaStorage = lambda: S3Boto3StorageOffload(  # NOQA: E731
    bucket_name=settings.MEDIAFILES_BUCKET,
    querystring_auth=True,
    querystring_expire=300,
    default_acl="private",
    secure_urls=False,
    url_protocol="",
    custom_domain=_MEDIA_CUSTOM_DOMAIN,
)
