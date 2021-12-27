# pylint: disable=invalid-name

from __future__ import unicode_literals

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="roletype",
            name="end_time",
            field=models.TimeField(default=datetime.time(10, 0)),
        ),
        migrations.AddField(
            model_name="roletype",
            name="start_time",
            field=models.TimeField(default=datetime.time(9, 30)),
        ),
    ]
