# pylint: disable=invalid-name

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [("extendedsites", "0001_initial"), ("extendedsites", "0002_indexes")]

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
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="extra",
                        serialize=False,
                        to="sites.site",
                        verbose_name="site",
                    ),
                ),
                ("subtitle", models.CharField(blank=True, max_length=256, null=True, verbose_name="subtitle")),
                ("description", models.CharField(blank=True, max_length=256, null=True, verbose_name="description")),
            ],
            options={"verbose_name": "Extended Site", "verbose_name_plural": "Extended Sites"},
        ),
        migrations.CreateModel(
            name="Keyword",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.CharField(max_length=64, verbose_name="value")),
                ("order", models.SmallIntegerField(blank=True, null=True, verbose_name="order")),
                (
                    "site",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="keywords",
                        to="extendedsites.extendedsite",
                        verbose_name="site",
                    ),
                ),
            ],
            options={"ordering": ["order", "value"], "verbose_name": "Keyword", "verbose_name_plural": "Keywords"},
        ),
        migrations.AddIndex(
            model_name="keyword",
            index=models.Index(fields=["order", "value"], name="extendedsit_order_4c95b0_idx"),
        ),
    ]
