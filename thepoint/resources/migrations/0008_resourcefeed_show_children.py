# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0007_podcasts"),
    ]

    operations = [
        migrations.AddField(
            model_name="resourcefeed",
            name="show_children",
            field=models.BooleanField(default=False, verbose_name="show children"),
        ),
    ]
