# pylint: disable=invalid-name

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def set_owner_from_author(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    Resource = apps.get_model("resources", "Resource")
    resources = Resource.objects.using(db_alias).exclude(author__isnull=True)
    for obj in resources:
        if obj.author.user:
            obj.owner = obj.author.user
    Resource.objects.bulk_update(resources, ["owner"])


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0008_expand_field_limits"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="resource",
            options={
                "get_latest_by": "published",
                "ordering": ["-published"],
                "permissions": [
                    ("publish_resource", "Can publish a resource"),
                    ("edit_own_resource", "Can only change a resource you own"),
                ],
                "verbose_name": "resource",
                "verbose_name_plural": "resources",
            },
        ),
        migrations.AddField(
            model_name="resource",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="resources",
                to=settings.AUTH_USER_MODEL,
                verbose_name="owner",
            ),
        ),
        migrations.RunPython(set_owner_from_author, migrations.RunPython.noop),
    ]
