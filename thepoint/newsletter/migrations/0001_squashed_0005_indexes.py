# pylint: disable=invalid-name

import datetime

import django.db.models.deletion
from django.db import migrations, models

import thepoint.newsletter.models


class Migration(migrations.Migration):

    replaces = [
        ("newsletter", "0001_initial"),
        ("newsletter", "0002_localise_strings"),
        ("newsletter", "0003_fix_publication_field"),
        ("newsletter", "0004_set_on_delete"),
        ("newsletter", "0005_indexes"),
    ]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Publication",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(unique=True, verbose_name="slug")),
                ("name", models.CharField(max_length=64, verbose_name="name")),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                ("mime_types", models.CharField(blank=True, max_length=256, null=True, verbose_name="MIME types")),
                ("is_private", models.BooleanField(default=False, verbose_name="private")),
                (
                    "publication_day",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("0", "Monday"),
                            ("1", "Tuesday"),
                            ("2", "Wednesday"),
                            ("3", "Thursday"),
                            ("4", "Friday"),
                            ("5", "Saturday"),
                            ("6", "Sunday"),
                        ],
                        max_length=1,
                        null=True,
                        verbose_name="publication day",
                    ),
                ),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "publications", "verbose_name": "publication"},
        ),
        migrations.CreateModel(
            name="Issue",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField(default=datetime.date.today, verbose_name="date")),
                ("slug", models.SlugField(editable=False, verbose_name="slug")),
                ("file", models.FileField(upload_to=thepoint.newsletter.models.get_filename, verbose_name="file")),
                ("mime_type", models.CharField(editable=False, max_length=128, verbose_name="MIME type")),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                (
                    "publication",
                    models.ForeignKey(
                        default=thepoint.newsletter.models.default_publication,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="issues",
                        to="newsletter.publication",
                        unique_for_date="date",
                        verbose_name="publication",
                    ),
                ),
            ],
            options={
                "ordering": ["-date"],
                "get_latest_by": "date",
                "verbose_name_plural": "issues",
                "verbose_name": "issue",
            },
        ),
        migrations.AddIndex(
            model_name="issue", index=models.Index(fields=["date"], name="newsletter__date_969234_idx"),
        ),
    ]
