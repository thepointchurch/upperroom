# pylint: disable=invalid-name

import uuid

from django.db import migrations, models


def set_family_uuid(apps, schema_editor):
    """set the Family uuid column"""

    db_alias = schema_editor.connection.alias
    Family = apps.get_model("directory", "Family")
    for obj in Family.objects.using(db_alias).all():
        obj.uuid = uuid.uuid4()
        obj.save()


def set_person_uuid(apps, schema_editor):
    """set the Person uuid column"""

    db_alias = schema_editor.connection.alias
    Person = apps.get_model("directory", "Person")
    for obj in Person.objects.using(db_alias).all():
        obj.uuid = uuid.uuid4()
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("directory", "0004_family_is_archived"),
    ]

    operations = [
        migrations.AlterField(
            model_name="family",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="person",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AddField(
            model_name="family",
            name="uuid",
            field=models.UUIDField(default=None, null=True, verbose_name="UUID"),
        ),
        migrations.RunPython(set_family_uuid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="family",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.AddField(
            model_name="person",
            name="uuid",
            field=models.UUIDField(default=None, null=True, verbose_name="UUID"),
        ),
        migrations.RunPython(set_person_uuid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="person",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
    ]
