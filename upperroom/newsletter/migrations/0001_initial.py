# pylint: disable=invalid-name

from __future__ import unicode_literals

import datetime

from django.db import migrations, models

from upperroom import newsletter


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Issue",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("date", models.DateField(default=datetime.date.today)),
                ("slug", models.SlugField(editable=False)),
                ("file", models.FileField(upload_to=newsletter.models.get_filename)),
                ("mime_type", models.CharField(max_length=128, editable=False)),
                ("description", models.TextField(null=True, blank=True)),
            ],
            options={"ordering": ["-date"], "get_latest_by": "date", "verbose_name_plural": "issues"},
        ),
        migrations.CreateModel(
            name="Publication",
            fields=[
                ("id", models.AutoField(verbose_name="ID", auto_created=True, serialize=False, primary_key=True)),
                ("slug", models.SlugField(unique=True)),
                ("name", models.CharField(max_length=64)),
                ("description", models.TextField(null=True, blank=True)),
                ("mime_types", models.CharField(max_length=256, null=True, blank=True)),
                ("is_private", models.BooleanField(default=False, verbose_name="Private")),
                (
                    "publication_day",
                    models.CharField(
                        max_length=1,
                        choices=[
                            ("0", "Monday"),
                            ("1", "Tuesday"),
                            ("2", "Wednesday"),
                            ("3", "Thursday"),
                            ("4", "Friday"),
                            ("5", "Saturday"),
                            ("6", "Sunday"),
                        ],
                        null=True,
                        blank=True,
                    ),
                ),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "publications"},
        ),
        migrations.AddField(
            model_name="issue",
            name="publication",
            field=models.ForeignKey(
                related_name="issues",
                default=newsletter.models.default_publication,
                to="newsletter.Publication",
                on_delete=models.PROTECT,
                unique_for_date="date",
            ),
        ),
    ]
