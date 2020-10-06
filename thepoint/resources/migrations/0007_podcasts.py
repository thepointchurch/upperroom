# pylint: disable=invalid-name
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models

import thepoint.resources as resources


def set_published_from_created(apps, schema_editor):
    _ = schema_editor
    Resource = apps.get_model("resources", "Resource")
    for resource in Resource.objects.filter(is_published=True).iterator():
        resource.published = resource.created
        resource.save()


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0006_update_ordering"),
    ]

    operations = [
        migrations.CreateModel(
            name="ResourceFeed",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("title", models.CharField(verbose_name="title", max_length=64)),
                ("slug", models.SlugField(verbose_name="slug")),
                ("description", models.TextField(verbose_name="description", null=True, blank=True)),
                (
                    "mime_type_list",
                    models.CharField(
                        verbose_name="MIME types",
                        help_text=(
                            "A comma-separated list of MIME types. "
                            "Only items with attachments ofthe given MIME types will appear in the feed."
                        ),
                        max_length=256,
                        validators=[
                            django.core.validators.RegexValidator(regex="^([\\w+-]+/[\\w+-]+,)*([\\w+-]+/[\\w+-]+)?$"),
                        ],
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "category_list",
                    models.CharField(
                        verbose_name="categories",
                        help_text="A comma-separated list of category names to apply to the feed.",
                        max_length=256,
                        validators=[django.core.validators.RegexValidator(regex="^([^,]+,)*([^,]+)?$")],
                        null=True,
                        blank=True,
                    ),
                ),
                ("copyright", models.CharField(verbose_name="copyright", max_length=128, null=True, blank=True)),
                (
                    "artwork",
                    models.FileField(
                        verbose_name="artwork",
                        upload_to=resources.models.get_feed_artwork_filename,
                        null=True,
                        blank=True,
                    ),
                ),
                ("is_podcast", models.BooleanField(verbose_name="podcast", default=False)),
                ("owner_name", models.CharField(verbose_name="owner name", max_length=64, null=True, blank=True)),
                ("owner_email", models.CharField(verbose_name="owner email", max_length=64, null=True, blank=True)),
                (
                    "tags",
                    models.ManyToManyField(verbose_name="tags", related_name="feeds", to="resources.Tag", blank=True),
                ),
            ],
            options={"verbose_name_plural": "feeds", "ordering": ["title"], "verbose_name": "feed"},
        ),
        migrations.AlterModelOptions(
            name="resource",
            options={
                "get_latest_by": "published",
                "ordering": ["-published"],
                "verbose_name": "resource",
                "verbose_name_plural": "resources",
            },
        ),
        migrations.AddField(
            model_name="attachment",
            name="metadata",
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name="metadata"),
        ),
        migrations.AddField(
            model_name="resource",
            name="published",
            field=models.DateTimeField(blank=True, null=True, verbose_name="published"),
        ),
        migrations.RunPython(set_published_from_created, elidable=True),
    ]
