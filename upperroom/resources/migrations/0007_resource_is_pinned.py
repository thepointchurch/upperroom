# pylint: disable=invalid-name
from django.db import migrations, models

from upperroom.resources.featureditem import SQL_CREATE, SQL_DROP


class Migration(migrations.Migration):
    dependencies = [
        ("resources", "0006_add_publish_permission"),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_DROP),
        migrations.AddField(
            model_name="resource",
            name="is_pinned",
            field=models.BooleanField(default=False, verbose_name="pinned"),
        ),
        migrations.RunSQL(sql=SQL_CREATE),
    ]
