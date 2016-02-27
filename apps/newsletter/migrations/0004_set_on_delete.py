from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import newsletter.models


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0003_fix_publication_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='publication',
            field=models.ForeignKey(
                default=newsletter.models.default_publication,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='issues',
                to='newsletter.Publication',
                unique_for_date='date',
                verbose_name='publication',
            ),
        ),
    ]
