# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0002_expand_family_street'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='email',
            field=models.EmailField(null=True, max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(null=True, max_length=254, blank=True),
        ),
    ]
