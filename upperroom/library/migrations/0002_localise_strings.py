# pylint: disable=invalid-name

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("library", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="book",
            options={"ordering": ["title"], "verbose_name": "book", "verbose_name_plural": "books"},
        ),
        migrations.AlterField(
            model_name="book",
            name="author",
            field=models.CharField(max_length=128, null=True, blank=True, verbose_name="author"),
        ),
        migrations.AlterField(
            model_name="book",
            name="description",
            field=models.TextField(null=True, blank=True, verbose_name="description"),
        ),
        migrations.AlterField(
            model_name="book",
            name="isbn",
            field=models.CharField(max_length=64, null=True, blank=True, verbose_name="ISBN"),
        ),
        migrations.AlterField(
            model_name="book",
            name="location",
            field=models.CharField(max_length=64, null=True, blank=True, verbose_name="location"),
        ),
        migrations.AlterField(
            model_name="book",
            name="subtitle",
            field=models.CharField(max_length=512, null=True, blank=True, verbose_name="subtitle"),
        ),
        migrations.AlterField(
            model_name="book",
            name="title",
            field=models.CharField(max_length=256, verbose_name="title"),
        ),
        migrations.AlterField(
            model_name="book",
            name="type",
            field=models.CharField(max_length=64, null=True, blank=True, verbose_name="type"),
        ),
    ]
