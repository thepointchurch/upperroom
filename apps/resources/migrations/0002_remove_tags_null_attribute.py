# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='tags',
            field=models.ManyToManyField(related_name='resources',
                                         to='resources.Tag',
                                         blank=True),
            preserve_default=True,
        ),
    ]
