# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='mime_type',
            field=models.CharField(max_length=128, editable=False),
            preserve_default=True,
        ),
    ]
