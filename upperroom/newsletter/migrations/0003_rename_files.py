# pylint: disable=invalid-name

import logging

from django.core.files import File
from django.core.files.storage import default_storage
from django.db import migrations, transaction

logger = logging.getLogger(__name__)


def rename_files(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Issue = apps.get_model("newsletter", "Issue")
    for obj in Issue.objects.using(db_alias).all():
        with transaction.atomic():
            old_name = obj.file.name
            obj.file = File(obj.file)
            obj.file.file.content_type = obj.mime_type
            try:
                obj.save()
                default_storage.delete(old_name)
            except FileNotFoundError:
                logger.warning("Issue file missing %s", old_name)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("newsletter", "0002_issue_uuid"),
    ]

    operations = [
        migrations.RunPython(rename_files, migrations.RunPython.noop),
    ]
