# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0002_show_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='priority',
            field=models.PositiveSmallIntegerField(
                help_text='A non-empty value will feature this item '
                          'in the main menu.',
                blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='priority',
            field=models.PositiveSmallIntegerField(
                help_text='A non-empty value will feature this item '
                          'in the main menu.',
                blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tag',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
