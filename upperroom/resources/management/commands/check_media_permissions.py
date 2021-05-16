from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from ....utils.storages import (
    decrypt_s3_file,
    encrypt_s3_file,
    is_s3_encrypted,
    is_s3_file,
    is_s3_file_public,
    set_s3_file_acl,
)
from ...models import Attachment, ResourceFeed


class Command(BaseCommand):
    help = "Check permissions and encryption on S3 media files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--test",
            action="store_true",
            dest="test",
            default=False,
            help=_("Do nothing, only show what would be done"),
        )

    def handle(self, *args, **options):
        for attachment in Attachment.objects.all():
            if not is_s3_file(attachment.file):
                continue
            self.fix_permission(attachment.file, not attachment.is_private, options["test"])
        for feed in ResourceFeed.objects.all():
            if not is_s3_file(feed.artwork):
                continue
            self.fix_permission(feed.artwork, True, options["test"])

    def fix_permission(self, file_object, is_public, dry_run=False):  # pylint: disable=too-many-branches
        if is_public:
            if is_s3_encrypted(file_object):
                if dry_run:
                    self.stdout.write(_("%(file_name)s will be decrypted") % {"file_name": file_object.name})
                else:
                    decrypt_s3_file(file_object)
                    self.stdout.write(_("%(file_name)s decrypted") % {"file_name": file_object.name})
            if not is_s3_file_public(file_object):
                if dry_run:
                    self.stdout.write(_("%(file_name)s will be set public") % {"file_name": file_object.name})
                else:
                    set_s3_file_acl(file_object, "public-read")
                    self.stdout.write(_("%(file_name)s set public") % {"file_name": file_object.name})
        else:
            if not is_s3_encrypted(file_object):
                if dry_run:
                    self.stdout.write(_("%(file_name)s will be encrypted") % {"file_name": file_object.name})
                else:
                    encrypt_s3_file(file_object)
                    self.stdout.write(_("%(file_name)s encrypted") % {"file_name": file_object.name})
            if is_s3_file_public(file_object):
                if dry_run:
                    self.stdout.write(_("%(file_name)s will be set private") % {"file_name": file_object.name})
                else:
                    set_s3_file_acl(file_object, "private")
                    self.stdout.write(_("%(file_name)s set private") % {"file_name": file_object.name})
