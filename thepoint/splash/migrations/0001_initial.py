# pylint: disable=invalid-name

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Splash",
            fields=[
                ("id", models.AutoField(verbose_name="ID", auto_created=True, primary_key=True, serialize=False)),
                ("title", models.CharField(verbose_name="title", max_length=256)),
                ("content", models.TextField(verbose_name="content", null=True, blank=True)),
                ("order", models.SmallIntegerField(verbose_name="order", null=True, blank=True)),
                (
                    "position",
                    models.CharField(
                        verbose_name="position", max_length=1, choices=[("A", "Above"), ("B", "Below")], default="A"
                    ),
                ),
                ("url", models.CharField(max_length=100, default="/")),
                ("is_current", models.BooleanField(verbose_name="current", default=True)),
                ("is_private", models.BooleanField(verbose_name="private", default=False)),
            ],
            options={
                "ordering": ["url", "position", "order", "title"],
                "verbose_name": "splash",
                "verbose_name_plural": "splashes",
            },
        ),
    ]
