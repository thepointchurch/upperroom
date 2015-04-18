# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0002_expand_roletype_verb'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='people',
            field=models.ManyToManyField(related_name='roles',
                                         to='directory.Person',
                                         blank=True),
            preserve_default=True,
        ),
    ]
