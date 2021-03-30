# pylint: disable=invalid-name
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0009_roster_builder"),
    ]

    operations = [
        migrations.AddField(
            model_name="roletype",
            name="include_in_print",
            field=models.BooleanField(default=True, verbose_name="include in printout"),
        ),
    ]
