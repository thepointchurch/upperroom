# pylint: disable=invalid-name

import django.contrib.postgres.fields.jsonb
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import upperroom.resources.models
from upperroom.resources.featureditem import SQL_CREATE, SQL_DROP


class Migration(migrations.Migration):

    replaces = [
        ("resources", "0001_initial"),
        ("resources", "0002_show_date"),
        ("resources", "0003_featured"),
        ("resources", "0004_localise_strings"),
        ("resources", "0005_set_on_delete"),
        ("resources", "0006_update_ordering"),
        ("resources", "0007_podcasts"),
        ("resources", "0008_resourcefeed_show_children"),
        ("resources", "0009_tag_is_private"),
        ("resources", "0010_indexes"),
        ("resources", "0011_jsonfield"),
        ("resources", "0012_featureditem"),
    ]

    initial = True

    dependencies = [
        ("directory", "0001_squashed_0007_indexes"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=64, verbose_name="name")),
                ("slug", models.SlugField(unique=True, verbose_name="slug")),
                (
                    "resources_per_page",
                    models.PositiveSmallIntegerField(
                        blank=True, default=10, null=True, verbose_name="resources per page"
                    ),
                ),
                ("reverse_order", models.BooleanField(default=False, verbose_name="reverse order")),
                ("is_exclusive", models.BooleanField(default=False, verbose_name="exclusive")),
                ("show_date", models.BooleanField(default=True, verbose_name="show date")),
                (
                    "priority",
                    models.PositiveSmallIntegerField(
                        blank=True, help_text="A non-empty value will feature this item in the main menu.", null=True
                    ),
                ),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                ("is_private", models.BooleanField(default=False, verbose_name="private")),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "tags", "verbose_name": "tag"},
        ),
        migrations.CreateModel(
            name="Resource",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=64, verbose_name="title")),
                ("slug", models.SlugField(unique=True, verbose_name="slug")),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                ("body", models.TextField(blank=True, null=True, verbose_name="body")),
                ("show_author", models.BooleanField(default=True, verbose_name="show author")),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="created")),
                ("modified", models.DateTimeField(auto_now=True, verbose_name="modified")),
                ("is_published", models.BooleanField(default=False, verbose_name="published")),
                ("is_private", models.BooleanField(default=False, verbose_name="private")),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="resources",
                        to="directory.person",
                        verbose_name="author",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="children",
                        to="resources.resource",
                        verbose_name="parent",
                    ),
                ),
                (
                    "tags",
                    models.ManyToManyField(
                        blank=True, related_name="resources", to="resources.Tag", verbose_name="tags"
                    ),
                ),
                ("show_date", models.BooleanField(default=True, verbose_name="show date")),
                (
                    "priority",
                    models.PositiveSmallIntegerField(
                        blank=True, help_text="A non-empty value will feature this item in the main menu.", null=True
                    ),
                ),
                ("published", models.DateTimeField(blank=True, null=True, verbose_name="published")),
            ],
            options={
                "ordering": ["-published"],
                "get_latest_by": "published",
                "verbose_name_plural": "resources",
                "verbose_name": "resource",
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
                    models.FileField(
                        upload_to=upperroom.resources.models.get_attachment_filename, verbose_name="file"
                    ),
                ),
                ("mime_type", models.CharField(editable=False, max_length=128, verbose_name="MIME type")),
                (
                    "kind",
                    models.CharField(
                        choices=[("A", "Alternate"), ("I", "Inline")], default="I", max_length=1, verbose_name="kind"
                    ),
                ),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                (
                    "resource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="resources.resource",
                        verbose_name="resource",
                    ),
                ),
                (
                    "metadata",
                    django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name="metadata"),
                ),
            ],
            options={
                "ordering": ["resource"],
                "verbose_name_plural": "attachments",
                "unique_together": {("resource", "slug")},
                "verbose_name": "attachment",
            },
        ),
        migrations.CreateModel(
            name="ResourceFeed",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=64, verbose_name="title")),
                ("slug", models.SlugField(verbose_name="slug")),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                (
                    "mime_type_list",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "A comma-separated list of MIME types. "
                            "Only items with attachments ofthe given MIME types will appear in the feed."
                        ),
                        max_length=256,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(regex="^([\\w+-]+/[\\w+-]+,)*([\\w+-]+/[\\w+-]+)?$")
                        ],
                        verbose_name="MIME types",
                    ),
                ),
                (
                    "category_list",
                    models.CharField(
                        blank=True,
                        help_text="A comma-separated list of category names to apply to the feed.",
                        max_length=256,
                        null=True,
                        validators=[django.core.validators.RegexValidator(regex="^([^,]+,)*([^,]+)?$")],
                        verbose_name="categories",
                    ),
                ),
                ("copyright", models.CharField(blank=True, max_length=128, null=True, verbose_name="copyright")),
                (
                    "artwork",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=upperroom.resources.models.get_feed_artwork_filename,
                        verbose_name="artwork",
                    ),
                ),
                ("is_podcast", models.BooleanField(default=False, verbose_name="podcast")),
                ("owner_name", models.CharField(blank=True, max_length=64, null=True, verbose_name="owner name")),
                ("owner_email", models.CharField(blank=True, max_length=64, null=True, verbose_name="owner email")),
                (
                    "tags",
                    models.ManyToManyField(blank=True, related_name="feeds", to="resources.Tag", verbose_name="tags"),
                ),
                ("show_children", models.BooleanField(default=False, verbose_name="show children")),
            ],
            options={"verbose_name_plural": "feeds", "ordering": ["title"], "verbose_name": "feed"},
        ),
        migrations.AddIndex(
            model_name="attachment",
            index=models.Index(fields=["kind"], name="resources_a_kind_34af54_idx"),
        ),
        migrations.AddIndex(
            model_name="resource",
            index=models.Index(fields=["published"], name="resources_r_publish_bb2046_idx"),
        ),
        migrations.AddIndex(
            model_name="resource",
            index=models.Index(fields=["is_published"], name="resources_r_is_publ_7afbcf_idx"),
        ),
        migrations.AddIndex(
            model_name="resource",
            index=models.Index(fields=["is_private"], name="resources_r_is_priv_ae0b21_idx"),
        ),
        migrations.AddIndex(
            model_name="tag",
            index=models.Index(fields=["name"], name="resources_t_name_352b9c_idx"),
        ),
        migrations.AddIndex(
            model_name="tag",
            index=models.Index(fields=["is_exclusive"], name="resources_t_is_excl_1f4322_idx"),
        ),
        migrations.AddIndex(
            model_name="tag",
            index=models.Index(fields=["is_private"], name="resources_t_is_priv_0f2454_idx"),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="metadata",
            field=models.JSONField(blank=True, null=True, verbose_name="metadata"),
        ),
        migrations.RunSQL(sql=SQL_CREATE, reverse_sql=SQL_DROP),
        migrations.CreateModel(
            name="FeaturedItem",
            fields=[
                ("title", models.CharField(max_length=64)),
                ("slug", models.SlugField(primary_key=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("priority", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("is_private", models.BooleanField()),
                ("type", models.CharField(choices=[("R", "Resource"), ("T", "Tag")], max_length=1)),
            ],
            options={"db_table": "resources_featureditem", "managed": False},
        ),
    ]
