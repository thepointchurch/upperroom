# pylint: disable=invalid-name
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExtendedSite",
            fields=[
                (
                    "site",
                    models.OneToOneField(
                        verbose_name="site",
                        to="sites.Site",
                        related_name="extra",
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("subtitle", models.CharField(verbose_name="subtitle", max_length=256, null=True, blank=True)),
                ("description", models.CharField(verbose_name="description", max_length=256, null=True, blank=True)),
            ],
            options={"verbose_name": "Extended Site", "verbose_name_plural": "Extended Sites"},
        ),
        migrations.CreateModel(
            name="Keyword",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("value", models.CharField(verbose_name="value", max_length=64)),
                ("order", models.SmallIntegerField(verbose_name="order", null=True, blank=True)),
                (
                    "site",
                    models.ForeignKey(
                        verbose_name="site",
                        to="extendedsites.ExtendedSite",
                        related_name="keywords",
                        on_delete=django.db.models.deletion.CASCADE,
                    ),
                ),
            ],
            options={"ordering": ["order", "value"], "verbose_name": "Keyword", "verbose_name_plural": "Keywords"},
        ),
    ]
