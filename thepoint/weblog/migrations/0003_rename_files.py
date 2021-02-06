# pylint: disable=invalid-name

import logging

from django.core.files import File
from django.core.files.storage import default_storage
from django.db import migrations, transaction

logger = logging.getLogger(__name__)


def rename_files(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Attachment = apps.get_model("weblog", "Attachment")
    for obj in Attachment.objects.using(db_alias).all():
        with transaction.atomic():
            old_name = obj.file.name
            obj.file = File(obj.file)
            try:
                obj.save()
                default_storage.delete(old_name)
            except FileNotFoundError:
                logger.warning("Attachment file missing %s", old_name)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("weblog", "0002_attachment_uuid"),
    ]

    operations = [
        migrations.RunPython(rename_files, migrations.RunPython.noop),
    ]
