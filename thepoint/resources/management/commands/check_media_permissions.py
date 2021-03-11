from django.core.management.base import BaseCommand

from ....utils.storages import (
    decrypt_s3_file,
    encrypt_s3_file,
    is_s3_encrypted,
    is_s3_file,
    is_s3_file_public,
    set_s3_file_acl,
)
from ...models import Attachment, ResourceFeed


def fix_permission(file_object, is_public):
    if is_public:
        if is_s3_encrypted(file_object):
            decrypt_s3_file(file_object)
        if not is_s3_file_public(file_object):
            set_s3_file_acl(file_object, "public-read")
    else:
        if not is_s3_encrypted(file_object):
            encrypt_s3_file(file_object)
        if is_s3_file_public(file_object):
            set_s3_file_acl(file_object, "private")


class Command(BaseCommand):
    help = "Check permissions and encryption on S3 media files."

    def handle(self, *args, **options):
        for attachment in Attachment.objects.all():
            print(attachment.title)
            if not is_s3_file(attachment.file):
                continue
            fix_permission(attachment.file, not attachment.is_private)
        for feed in ResourceFeed.objects.all():
            print(feed.title)
            if not is_s3_file(feed.artwork):
                continue
            fix_permission(feed.artwork, True)
