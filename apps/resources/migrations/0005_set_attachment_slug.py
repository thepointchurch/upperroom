# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils.text import slugify


def set_attachment_slug(apps, schema_editor):
    Attachment = apps.get_model('resources', 'Attachment')
    db_alias = schema_editor.connection.alias
    for attachment in Attachment.objects.using(db_alias):
        attachment.slug = slugify(attachment.title)
        attachment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0004_add_attachment_slug'),
    ]

    operations = [
        migrations.RunPython(set_attachment_slug),
    ]
