# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0005_set_on_delete'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resource',
            options={
                'get_latest_by': 'created',
                'ordering': ['-created'],
                'verbose_name': 'resource',
                'verbose_name_plural': 'resources',
            },
        ),
    ]
