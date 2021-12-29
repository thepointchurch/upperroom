# pylint: disable=invalid-name
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0005_tag_slug_prefix"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="resource",
            options={
                "get_latest_by": "published",
                "ordering": ["-published"],
                "permissions": [("publish_resource", "Can publish a resource")],
                "verbose_name": "resource",
                "verbose_name_plural": "resources",
            },
        ),
    ]
