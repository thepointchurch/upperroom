# pylint: disable=invalid-name

import datetime

import django.db.models.deletion
import django.db.models.manager
from django.db import migrations, models

import upperroom.roster.models


class Migration(migrations.Migration):

    replaces = [
        ("roster", "0001_initial"),
        ("roster", "0002_roletype_add_times"),
        ("roster", "0003_localise_strings"),
        ("roster", "0004_set_on_delete"),
        ("roster", "0005_update_roles_relation"),
        ("roster", "0006_roletype_parent"),
        ("roster", "0007_roletype_servers"),
        ("roster", "0008_meeting_templates"),
        ("roster", "0009_roster_builder"),
        ("roster", "0010_roletype_include_in_print"),
        ("roster", "0011_indexes"),
        ("roster", "0012_pastmeeting"),
    ]

    initial = True

    dependencies = [
        ("directory", "0001_squashed_0007_indexes"),
    ]

    operations = [
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=30, verbose_name="name")),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "locations", "verbose_name": "location"},
        ),
        migrations.CreateModel(
            name="Meeting",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "date",
                    models.DateField(
                        default=upperroom.roster.models.next_empty_meeting_date, unique=True, verbose_name="date"
                    ),
                ),
            ],
            options={
                "ordering": ["date"],
                "get_latest_by": "date",
                "verbose_name_plural": "meetings",
                "verbose_name": "meeting",
            },
        ),
        migrations.CreateModel(
            name="RoleType",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=30, verbose_name="name")),
                ("verb", models.CharField(max_length=50, verbose_name="verb")),
                ("order", models.PositiveSmallIntegerField(default=100, verbose_name="order")),
                ("end_time", models.TimeField(default=datetime.time(10, 0), verbose_name="end time")),
                ("start_time", models.TimeField(default=datetime.time(9, 30), verbose_name="start time")),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="roster.roletype",
                        verbose_name="parent",
                    ),
                ),
                (
                    "servers",
                    models.ManyToManyField(
                        blank=True,
                        limit_choices_to={"is_current": True},
                        related_name="role_types",
                        to="directory.Person",
                        verbose_name="servers",
                    ),
                ),
                ("order_by_age", models.BooleanField(default=True, verbose_name="order by age")),
                ("include_in_print", models.BooleanField(default=True, verbose_name="include in printout")),
            ],
            options={"ordering": ["order"], "verbose_name_plural": "role types", "verbose_name": "role type"},
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("timestamp", models.DateTimeField(auto_now=True, verbose_name="timestamp")),
                ("revision", models.PositiveIntegerField(default=0, verbose_name="revision")),
                ("guest", models.CharField(blank=True, max_length=30, null=True, verbose_name="guest")),
                ("description", models.CharField(blank=True, max_length=64, null=True, verbose_name="description")),
                (
                    "location",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="roles",
                        to="roster.location",
                        verbose_name="location",
                    ),
                ),
                (
                    "meeting",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roles",
                        to="roster.meeting",
                        verbose_name="meeting",
                    ),
                ),
                (
                    "people",
                    models.ManyToManyField(
                        blank=True,
                        limit_choices_to={"is_current": True},
                        related_name="roles",
                        to="directory.Person",
                        verbose_name="people",
                    ),
                ),
                (
                    "role",
                    models.ForeignKey(
                        limit_choices_to=models.Q(children__isnull=True),
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="roles",
                        to="roster.roletype",
                        verbose_name="role",
                    ),
                ),
            ],
            options={"ordering": ["role"], "verbose_name_plural": "roles", "verbose_name": "role"},
        ),
        migrations.AlterModelManagers(
            name="meeting",
            managers=[("current_objects", django.db.models.manager.Manager())],
        ),
        migrations.AlterModelManagers(name="role", managers=[]),
        migrations.CreateModel(
            name="MeetingTemplate",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=30, verbose_name="name")),
                (
                    "week_day",
                    models.SmallIntegerField(
                        blank=True,
                        choices=[
                            (1, "Sunday"),
                            (2, "Monday"),
                            (3, "Tuesday"),
                            (4, "Wednesday"),
                            (5, "Thursday"),
                            (6, "Friday"),
                            (7, "Saturday"),
                        ],
                        null=True,
                        verbose_name="week day",
                    ),
                ),
                ("is_default", models.BooleanField(default=False, verbose_name="is default")),
            ],
            options={
                "verbose_name_plural": "meeting templates",
                "verbose_name": "meeting template",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="RoleTypeTemplateMapping",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.SmallIntegerField(blank=True, null=True, verbose_name="order")),
                ("role_type", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="roster.roletype")),
                (
                    "template",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="roster.meetingtemplate"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="meetingtemplate",
            name="roles",
            field=models.ManyToManyField(
                blank=True,
                related_name="templates",
                through="roster.RoleTypeTemplateMapping",
                to="roster.RoleType",
                verbose_name="roles",
            ),
        ),
        migrations.CreateModel(
            name="PastMeeting",
            fields=[],
            options={"proxy": True, "indexes": [], "constraints": []},
            bases=("roster.meeting",),
            managers=[("current_objects", django.db.models.manager.Manager())],
        ),
        migrations.AddIndex(
            model_name="roletype",
            index=models.Index(fields=["order"], name="roster_role_order_42d3b6_idx"),
        ),
    ]
