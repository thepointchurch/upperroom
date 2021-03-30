# pylint: disable=invalid-name

from __future__ import unicode_literals

from django.db import migrations, models

import upperroom.resources as resources


class Migration(migrations.Migration):

    dependencies = [
        ("resources", "0003_featured"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="attachment",
            options={"ordering": ["resource"], "verbose_name": "attachment", "verbose_name_plural": "attachments"},
        ),
        migrations.AlterModelOptions(
            name="resource",
            options={
                "get_latest_by": "created",
                "ordering": ["created"],
                "verbose_name": "resource",
                "verbose_name_plural": "resources",
            },
        ),
        migrations.AlterModelOptions(
            name="tag", options={"ordering": ["name"], "verbose_name": "tag", "verbose_name_plural": "tags"},
        ),
        migrations.AlterField(
            model_name="attachment",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="description"),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="file",
            field=models.FileField(upload_to=resources.models.get_attachment_filename, verbose_name="file"),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="kind",
            field=models.CharField(
                max_length=1, choices=[("A", "Alternate"), ("I", "Inline")], default="I", verbose_name="kind",
            ),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="mime_type",
            field=models.CharField(max_length=128, editable=False, verbose_name="MIME type"),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="resource",
            field=models.ForeignKey(
                to="resources.Resource", on_delete=models.CASCADE, related_name="attachments", verbose_name="resource",
            ),
        ),
        migrations.AlterField(model_name="attachment", name="slug", field=models.SlugField(verbose_name="slug")),
        migrations.AlterField(
            model_name="attachment", name="title", field=models.CharField(max_length=64, verbose_name="title"),
        ),
        migrations.AlterField(
            model_name="resource",
            name="author",
            field=models.ForeignKey(
                blank=True,
                to="directory.Person",
                on_delete=models.SET_NULL,
                related_name="resources",
                null=True,
                verbose_name="author",
            ),
        ),
        migrations.AlterField(
            model_name="resource", name="body", field=models.TextField(blank=True, null=True, verbose_name="body"),
        ),
        migrations.AlterField(
            model_name="resource",
            name="created",
            field=models.DateTimeField(auto_now_add=True, verbose_name="created"),
        ),
        migrations.AlterField(
            model_name="resource",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="description"),
        ),
        migrations.AlterField(
            model_name="resource", name="is_private", field=models.BooleanField(default=False, verbose_name="private"),
        ),
        migrations.AlterField(
            model_name="resource",
            name="is_published",
            field=models.BooleanField(default=False, verbose_name="published"),
        ),
        migrations.AlterField(
            model_name="resource", name="modified", field=models.DateTimeField(auto_now=True, verbose_name="modified"),
        ),
        migrations.AlterField(
            model_name="resource",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                to="resources.Resource",
                on_delete=models.SET_NULL,
                related_name="children",
                null=True,
                verbose_name="parent",
            ),
        ),
        migrations.AlterField(
            model_name="resource",
            name="show_author",
            field=models.BooleanField(default=True, verbose_name="show author"),
        ),
        migrations.AlterField(
            model_name="resource", name="show_date", field=models.BooleanField(default=True, verbose_name="show date"),
        ),
        migrations.AlterField(
            model_name="resource", name="slug", field=models.SlugField(unique=True, verbose_name="slug"),
        ),
        migrations.AlterField(
            model_name="resource",
            name="tags",
            field=models.ManyToManyField(
                blank=True, to="resources.Tag", related_name="resources", verbose_name="tags",
            ),
        ),
        migrations.AlterField(
            model_name="resource", name="title", field=models.CharField(max_length=64, verbose_name="title"),
        ),
        migrations.AlterField(
            model_name="tag",
            name="description",
            field=models.TextField(blank=True, null=True, verbose_name="description"),
        ),
        migrations.AlterField(
            model_name="tag", name="is_exclusive", field=models.BooleanField(default=False, verbose_name="exclusive"),
        ),
        migrations.AlterField(
            model_name="tag", name="name", field=models.CharField(max_length=64, verbose_name="name"),
        ),
        migrations.AlterField(
            model_name="tag",
            name="resources_per_page",
            field=models.PositiveSmallIntegerField(
                blank=True, default=10, null=True, verbose_name="resources per page",
            ),
        ),
        migrations.AlterField(
            model_name="tag",
            name="reverse_order",
            field=models.BooleanField(default=False, verbose_name="reverse order"),
        ),
        migrations.AlterField(
            model_name="tag", name="show_date", field=models.BooleanField(default=True, verbose_name="show date"),
        ),
        migrations.AlterField(
            model_name="tag", name="slug", field=models.SlugField(unique=True, verbose_name="slug"),
        ),
    ]
