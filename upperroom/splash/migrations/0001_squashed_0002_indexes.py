# pylint: disable=invalid-name

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [("splash", "0001_initial"), ("splash", "0002_indexes")]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Splash",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=256, verbose_name="title")),
                ("content", models.TextField(blank=True, null=True, verbose_name="content")),
                ("order", models.SmallIntegerField(blank=True, null=True, verbose_name="order")),
                (
                    "position",
                    models.CharField(
                        choices=[("A", "Above"), ("B", "Below")], default="A", max_length=1, verbose_name="position"
                    ),
                ),
                ("url", models.CharField(default="/", max_length=100)),
                ("is_current", models.BooleanField(default=True, verbose_name="current")),
                ("is_private", models.BooleanField(default=False, verbose_name="private")),
            ],
            options={
                "ordering": ["url", "position", "order", "title"],
                "verbose_name": "splash",
                "verbose_name_plural": "splashes",
            },
        ),
        migrations.AddIndex(
            model_name="splash",
            index=models.Index(fields=["is_current", "position"], name="splash_spla_is_curr_f96f12_idx"),
        ),
        migrations.AddIndex(
            model_name="splash",
            index=models.Index(fields=["url", "position", "order", "title"], name="splash_spla_url_e4ebd5_idx"),
        ),
    ]
