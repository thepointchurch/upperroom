# pylint: disable=invalid-name

import logging

from django.core.files import File
from django.core.files.storage import default_storage
from django.db import migrations, transaction

from thepoint.resources.models import get_attachment_filename
from thepoint.utils.storages import set_s3_file_acl

logger = logging.getLogger(__name__)


def rename_files(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Attachment = apps.get_model("resources", "Attachment")
    for obj in Attachment.objects.using(db_alias).all():
        with transaction.atomic():
            old_name = obj.file.name
            obj.file = File(obj.file)
            obj.file.file.content_type = obj.mime_type
            is_private = obj.resource.is_private or any(tag.is_private for tag in obj.resource.tags.all())
            if not is_private:
                obj.file.storage.save_cleartext(get_attachment_filename(obj, obj.file.name))
            try:
                obj.save()
                default_storage.delete(old_name)
            except FileNotFoundError:
                logger.warning("Attachment file missing %s", old_name)
                continue
            if not is_private:
                set_s3_file_acl(obj.file, "public-read")


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("resources", "0002_attachment_uuid"),
    ]

    operations = [
        migrations.RunPython(rename_files, migrations.RunPython.noop),
    ]
