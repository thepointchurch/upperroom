# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0002_remove_tags_null_attribute'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attachment',
            name='mime_type',
            field=models.CharField(max_length=128, editable=False),
            preserve_default=True,
        ),
    ]
