# pylint: disable=invalid-name

import uuid

from django.db import migrations, models


def set_uuid(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Attachment = apps.get_model("resources", "Attachment")
    for obj in Attachment.objects.using(db_alias).all():
        obj.uuid = uuid.uuid4()
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0001_squashed_0012_featureditem"),
    ]

    operations = [
        migrations.AddField(model_name="attachment", name="uuid", field=models.UUIDField(null=True),),
        migrations.RunPython(set_uuid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="attachment",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name="ID"
            ),
        ),
        migrations.RemoveField(model_name="attachment", name="id",),
        migrations.RenameField(model_name="attachment", old_name="uuid", new_name="id",),
    ]
