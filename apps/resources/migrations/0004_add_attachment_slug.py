# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0003_expand_attachment_mime_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='slug',
            field=models.SlugField(default=''),
            preserve_default=False,
        ),
    ]
