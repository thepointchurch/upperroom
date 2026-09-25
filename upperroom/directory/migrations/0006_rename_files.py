# pylint: disable=invalid-name

import logging

from django.core.files.images import ImageFile
from django.core.files.storage import default_storage
from django.db import migrations, transaction

logger = logging.getLogger(__name__)


def rename_files(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Family = apps.get_model("directory", "Family")
    for obj in Family.objects.using(db_alias).all():
        for field in ["photo", "photo_thumbnail"]:
            if not getattr(obj, field, None):
                continue
            with transaction.atomic():
                old_name = getattr(obj, field).name
                setattr(obj, field, ImageFile(obj.photo))
                try:
                    obj.save()
                    default_storage.delete(old_name)
                except FileNotFoundError:
                    logger.warning("Family photo file missing %s", old_name)


class Migration(migrations.Migration):

    dependencies = [
        ("directory", "0005_add_uuid_fields"),
    ]

    operations = [
        migrations.RunPython(rename_files, migrations.RunPython.noop),
    ]
