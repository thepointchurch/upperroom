from django.conf import settings
from storages.backends.s3boto import S3BotoStorage


_static_custom_domain = None
if '.' in settings.STATICFILES_BUCKET:
    _static_custom_domain = settings.STATICFILES_BUCKET

S3StaticStorage = lambda: S3BotoStorage(
    bucket_name=settings.STATICFILES_BUCKET,
    querystring_auth=False,
    secure_urls=False,
    url_protocol='',
    custom_domain=_static_custom_domain
)


class S3BotoStorageOffload(S3BotoStorage):
    try:
        offload = settings.MEDIAFILES_OFFLOAD
    except NameError:
        offload = Falsee

_media_custom_domain = None
if '.' in settings.MEDIAFILES_BUCKET:
    _media_custom_domain = settings.MEDIAFILES_BUCKET

S3MediaStorage = lambda: S3BotoStorageOffload(
    bucket_name=settings.MEDIAFILES_BUCKET,
    querystring_auth=True,
    querystring_expire=300,
    default_acl='private',
    secure_urls=False,
    url_protocol='',
    custom_domain=_media_custom_domain
)
