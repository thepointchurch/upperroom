# pylint: disable=invalid-name
from django.db import migrations, models

from upperroom.resources.featureditem import SQL_CREATE, SQL_DROP


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0004_bigautofield"),
    ]

    operations = [
        migrations.RunSQL(sql=SQL_DROP),
        migrations.AddField(
            model_name="tag",
            name="slug_prefix",
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name="slug prefix"),
        ),
        migrations.RunSQL(sql=SQL_CREATE),
    ]
