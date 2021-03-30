# pylint: disable=invalid-name

import django.db.models.deletion
from django.db import migrations, models

import upperroom.weblog.models


class Migration(migrations.Migration):

    replaces = [("weblog", "0001_initial"), ("weblog", "0002_indexes"), ("weblog", "0003_attachment_description")]

    initial = True

    dependencies = [
        ("directory", "0001_squashed_0007_indexes"),
    ]

    operations = [
        migrations.CreateModel(
            name="WeblogEntry",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=64, verbose_name="title")),
                ("slug", models.SlugField(unique_for_month="created", verbose_name="slug")),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                ("body", models.TextField(blank=True, null=True, verbose_name="body")),
                ("show_author", models.BooleanField(default=True, verbose_name="show author")),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="created")),
                ("modified", models.DateTimeField(auto_now=True, verbose_name="modified")),
                ("published", models.DateTimeField(blank=True, null=True, verbose_name="published")),
                ("show_date", models.BooleanField(default=True, verbose_name="show date")),
                ("is_published", models.BooleanField(default=False, verbose_name="published")),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="weblogs",
                        to="directory.person",
                        verbose_name="author",
                    ),
                ),
            ],
            options={
                "ordering": ["-published"],
                "get_latest_by": "published",
                "verbose_name": "weblog entry",
                "verbose_name_plural": "weblog entries",
            },
        ),
        migrations.CreateModel(
            name="Attachment",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=64, verbose_name="title")),
                ("slug", models.SlugField(verbose_name="slug")),
                (
                    "file",
                    models.FileField(upload_to=upperroom.weblog.models.get_attachment_filename, verbose_name="file"),
                ),
                ("mime_type", models.CharField(editable=False, max_length=128, verbose_name="MIME type")),
                (
                    "kind",
                    models.CharField(
                        choices=[("A", "Alternate"), ("I", "Inline")], default="I", max_length=1, verbose_name="kind"
                    ),
                ),
                (
                    "entry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="weblog.weblogentry",
                        verbose_name="entry",
                    ),
                ),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
            ],
            options={
                "verbose_name": "attachment",
                "verbose_name_plural": "attachments",
                "ordering": ["entry"],
                "unique_together": {("entry", "slug")},
            },
        ),
        migrations.AddIndex(
            model_name="attachment",
            index=models.Index(fields=["entry_id", "kind"], name="weblog_atta_entry_i_9e8c2b_idx"),
        ),
        migrations.AddIndex(
            model_name="weblogentry", index=models.Index(fields=["published"], name="weblog_webl_publish_d624e8_idx"),
        ),
        migrations.AddIndex(
            model_name="weblogentry",
            index=models.Index(fields=["is_published"], name="weblog_webl_is_publ_7ad033_idx"),
        ),
    ]
