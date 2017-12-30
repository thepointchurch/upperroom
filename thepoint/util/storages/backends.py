from urllib.parse import urlsplit

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

_static_custom_domain = None
if '.' in settings.STATICFILES_BUCKET:
    _static_custom_domain = settings.STATICFILES_BUCKET

S3StaticStorage = lambda: S3Boto3Storage(  # noqa
    bucket_name=settings.STATICFILES_BUCKET,
    querystring_auth=False,
    secure_urls=False,
    url_protocol='',
    custom_domain=_static_custom_domain
)


class S3Boto3StorageOffload(S3Boto3Storage):
    try:
        offload = settings.MEDIAFILES_OFFLOAD
    except (AttributeError, NameError):
        offload = False

    def url(self, name, headers=None, response_headers=None):
        # Generate the S3 offload URL but enforce our protocol and domain
        name = self._normalize_name(self._clean_name(name))
        url = self.connection.generate_url(self.querystring_expire,
                                           method='GET',
                                           bucket=self.bucket.name,
                                           key=self._encode_name(name),
                                           headers=headers,
                                           query_auth=self.querystring_auth,
                                           force_http=False,
                                           response_headers=response_headers)
        url = urlsplit(url)
        domain = self.custom_domain or url.netloc
        return '%s//%s%s?%s' % (self.url_protocol,
                                domain,
                                url.path,
                                url.query)


_media_custom_domain = None
if '.' in settings.MEDIAFILES_BUCKET:
    _media_custom_domain = settings.MEDIAFILES_BUCKET

S3MediaStorage = lambda: S3Boto3StorageOffload(  # noqa
    bucket_name=settings.MEDIAFILES_BUCKET,
    querystring_auth=True,
    querystring_expire=300,
    default_acl='private',
    secure_urls=False,
    url_protocol='',
    custom_domain=_media_custom_domain
)
