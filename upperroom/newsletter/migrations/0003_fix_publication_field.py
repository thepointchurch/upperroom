# pylint: disable=invalid-name

from __future__ import unicode_literals

from django.db import migrations, models

from upperroom import newsletter


class Migration(migrations.Migration):

    dependencies = [
        ("newsletter", "0002_localise_strings"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issue",
            name="publication",
            field=models.ForeignKey(
                to="newsletter.Publication",
                on_delete=models.PROTECT,
                default=newsletter.models.default_publication,
                unique_for_date="date",
                verbose_name="publication",
                related_name="issues",
            ),
        ),
    ]
