# pylint: disable=invalid-name

import uuid

from django.db import migrations, models


def set_uuid(apps, schema_editor):
    """set the WeblogEntry uuid column"""

    db_alias = schema_editor.connection.alias
    WeblogEntry = apps.get_model("weblog", "WeblogEntry")
    for obj in WeblogEntry.objects.using(db_alias).all():
        obj.uuid = uuid.uuid4()
        obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ("weblog", "0005_expand_field_limits"),
    ]

    operations = [
        migrations.AddField(
            model_name="weblogentry",
            name="uuid",
            field=models.UUIDField(default=None, null=True, verbose_name="UUID"),
        ),
        migrations.RunPython(set_uuid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="weblogentry",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.AlterField(
            model_name="weblogentry",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID"),
        ),
    ]
