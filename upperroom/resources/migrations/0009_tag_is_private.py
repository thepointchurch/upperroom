# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0008_resourcefeed_show_children"),
    ]

    operations = [
        migrations.AddField(
            model_name="tag",
            name="is_private",
            field=models.BooleanField(default=False, verbose_name="private"),
        ),
    ]
