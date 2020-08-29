# pylint: disable=invalid-name
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("roster", "0007_roletype_servers"),
    ]

    operations = [
        migrations.CreateModel(
            name="MeetingTemplate",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=30, verbose_name="name")),
                (
                    "week_day",
                    models.SmallIntegerField(
                        choices=[
                            (1, "Sunday"),
                            (2, "Monday"),
                            (3, "Tuesday"),
                            (4, "Wednesday"),
                            (5, "Thursday"),
                            (6, "Friday"),
                            (7, "Saturday"),
                        ],
                        blank=True,
                        null=True,
                        verbose_name="week day",
                    ),
                ),
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
                ("role_type", models.ForeignKey(to="roster.RoleType", on_delete=django.db.models.deletion.CASCADE)),
                (
                    "template",
                    models.ForeignKey(to="roster.MeetingTemplate", on_delete=django.db.models.deletion.CASCADE),
                ),
            ],
        ),
        migrations.AddField(
            model_name="meetingtemplate",
            name="roles",
            field=models.ManyToManyField(
                to="roster.RoleType",
                through="roster.RoleTypeTemplateMapping",
                blank=True,
                related_name="templates",
                verbose_name="roles",
            ),
        ),
    ]
