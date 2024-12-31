# pylint: disable=invalid-name
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("directory", "0004_family_is_archived"),
        ("roster", "0003_expand_field_limits"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExclusionPerson",
            fields=[],
            options={
                "verbose_name": "server exclusion date",
                "verbose_name_plural": "exclusion dates",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("directory.person",),
        ),
        migrations.CreateModel(
            name="RosterExclusion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(verbose_name="date")),
                (
                    "person",
                    models.ForeignKey(
                        limit_choices_to={"is_current": True},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exclusions",
                        to="directory.person",
                        verbose_name="exclusion",
                    ),
                ),
            ],
            options={
                "verbose_name": "exclusion date",
                "verbose_name_plural": "exclusion dates",
                "constraints": [models.UniqueConstraint(fields=("person", "date"), name="roster_exclusion_unique")],
            },
        ),
    ]
