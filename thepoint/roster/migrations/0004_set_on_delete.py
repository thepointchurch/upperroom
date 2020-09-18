# pylint: disable=invalid-name
from __future__ import unicode_literals

import django.db.models.deletion
import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0003_localise_strings"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="meeting", managers=[("current_objects", django.db.models.manager.Manager())],
        ),
        migrations.AlterModelManagers(
            name="role", managers=[("current_objects", django.db.models.manager.Manager())],
        ),
        migrations.AlterField(
            model_name="role",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.PROTECT,
                related_name="roles",
                to="roster.Location",
                verbose_name="location",
            ),
        ),
        migrations.AlterField(
            model_name="role",
            name="role",
            field=models.ForeignKey(
                on_delete=models.PROTECT, related_name="roles", to="roster.RoleType", verbose_name="role",
            ),
        ),
    ]
