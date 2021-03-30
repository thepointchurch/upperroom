# pylint: disable=invalid-name

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [("library", "0001_initial"), ("library", "0002_localise_strings")]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=256, verbose_name="title")),
                ("subtitle", models.CharField(blank=True, max_length=512, null=True, verbose_name="subtitle")),
                ("description", models.TextField(blank=True, null=True, verbose_name="description")),
                ("type", models.CharField(blank=True, max_length=64, null=True, verbose_name="type")),
                ("author", models.CharField(blank=True, max_length=128, null=True, verbose_name="author")),
                ("isbn", models.CharField(blank=True, max_length=64, null=True, verbose_name="ISBN")),
                ("location", models.CharField(blank=True, max_length=64, null=True, verbose_name="location")),
            ],
            options={"ordering": ["title"], "verbose_name_plural": "books", "verbose_name": "book"},
        ),
    ]
