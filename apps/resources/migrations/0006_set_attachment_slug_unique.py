# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0005_set_attachment_slug'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attachment',
            unique_together=set([('resource', 'slug')]),
        ),
    ]
