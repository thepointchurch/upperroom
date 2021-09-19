# pylint: disable=invalid-name

from __future__ import unicode_literals

import datetime

from django.db import migrations, models

from upperroom import roster


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0002_roletype_add_times"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="location",
            options={"ordering": ["name"], "verbose_name": "location", "verbose_name_plural": "locations"},
        ),
        migrations.AlterModelOptions(
            name="meeting",
            options={
                "get_latest_by": "date",
                "ordering": ["date"],
                "verbose_name": "meeting",
                "verbose_name_plural": "meetings",
            },
        ),
        migrations.AlterModelOptions(
            name="role", options={"ordering": ["role"], "verbose_name": "role", "verbose_name_plural": "roles"},
        ),
        migrations.AlterModelOptions(
            name="roletype",
            options={"ordering": ["order"], "verbose_name": "role type", "verbose_name_plural": "role types"},
        ),
        migrations.AlterField(
            model_name="location", name="name", field=models.CharField(verbose_name="name", max_length=30),
        ),
        migrations.AlterField(
            model_name="meeting",
            name="date",
            field=models.DateField(verbose_name="date", default=roster.models.next_empty_meeting_date, unique=True),
        ),
        migrations.AlterField(
            model_name="role",
            name="description",
            field=models.CharField(blank=True, null=True, verbose_name="description", max_length=64),
        ),
        migrations.AlterField(
            model_name="role",
            name="guest",
            field=models.CharField(blank=True, null=True, verbose_name="guest", max_length=30),
        ),
        migrations.AlterField(
            model_name="role",
            name="location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                related_name="roles",
                verbose_name="location",
                to="roster.Location",
                on_delete=models.PROTECT,
            ),
        ),
        migrations.AlterField(
            model_name="role",
            name="meeting",
            field=models.ForeignKey(
                verbose_name="meeting", related_name="roles", to="roster.Meeting", on_delete=models.CASCADE,
            ),
        ),
        migrations.AlterField(
            model_name="role",
            name="people",
            field=models.ManyToManyField(
                blank=True, verbose_name="people", related_name="roles", to="directory.Person",
            ),
        ),
        migrations.AlterField(
            model_name="role", name="revision", field=models.PositiveIntegerField(verbose_name="revision", default=0),
        ),
        migrations.AlterField(
            model_name="role",
            name="role",
            field=models.ForeignKey(
                verbose_name="role", related_name="roles", to="roster.RoleType", on_delete=models.PROTECT,
            ),
        ),
        migrations.AlterField(
            model_name="role", name="timestamp", field=models.DateTimeField(verbose_name="timestamp", auto_now=True),
        ),
        migrations.AlterField(
            model_name="roletype",
            name="end_time",
            field=models.TimeField(verbose_name="end time", default=datetime.time(10, 0)),
        ),
        migrations.AlterField(
            model_name="roletype", name="name", field=models.CharField(verbose_name="name", max_length=30),
        ),
        migrations.AlterField(
            model_name="roletype",
            name="order",
            field=models.PositiveSmallIntegerField(verbose_name="order", default=100),
        ),
        migrations.AlterField(
            model_name="roletype",
            name="start_time",
            field=models.TimeField(verbose_name="start time", default=datetime.time(9, 30)),
        ),
        migrations.AlterField(
            model_name="roletype", name="verb", field=models.CharField(verbose_name="verb", max_length=50),
        ),
    ]
