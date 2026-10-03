# pylint: disable=invalid-name

import uuid

from django.db import migrations, models

from upperroom.resources.featureditem import SQL_CREATE, SQL_DROP


def set_resource_uuid(apps, schema_editor):
    """set the Resource uuid column"""

    db_alias = schema_editor.connection.alias
    Resource = apps.get_model("resources", "Resource")
    for obj in Resource.objects.using(db_alias).all():
        obj.uuid = uuid.uuid4()
        obj.save()


def set_resourcefeed_uuid(apps, schema_editor):
    """set the ResourceFeed uuid column"""

    db_alias = schema_editor.connection.alias
    ResourceFeed = apps.get_model("resources", "ResourceFeed")
    for obj in ResourceFeed.objects.using(db_alias).all():
        obj.uuid = uuid.uuid4()
        obj.save()


def set_tag_uuid(apps, schema_editor):
    """set the Tag uuid column"""

    db_alias = schema_editor.connection.alias
    Tag = apps.get_model("resources", "Tag")
    for obj in Tag.objects.using(db_alias).all():
        obj.uuid = uuid.uuid4()
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0009_add_resource_owner"),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_DROP),
        migrations.AlterField(
            model_name="resource",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="resourcefeed",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AlterField(
            model_name="tag",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID"),
        ),
        migrations.AddField(
            model_name="resource",
            name="uuid",
            field=models.UUIDField(default=None, null=True, verbose_name="UUID"),
        ),
        migrations.RunPython(set_resource_uuid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="resource",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.AddField(
            model_name="resourcefeed",
            name="uuid",
            field=models.UUIDField(default=None, null=True, verbose_name="UUID"),
        ),
        migrations.RunPython(set_resourcefeed_uuid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="resourcefeed",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.AddField(
            model_name="tag",
            name="uuid",
            field=models.UUIDField(default=None, null=True, verbose_name="UUID"),
        ),
        migrations.RunPython(set_tag_uuid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="tag",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.RunSQL(sql=SQL_CREATE),
    ]
