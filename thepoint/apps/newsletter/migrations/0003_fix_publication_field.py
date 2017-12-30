# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import thepoint.apps.newsletter as newsletter


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0002_localise_strings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='publication',
            field=models.ForeignKey(
                to='newsletter.Publication',
                default=newsletter.models.default_publication,
                unique_for_date='date',
                verbose_name='publication',
                related_name='issues',
            ),
        ),
    ]
