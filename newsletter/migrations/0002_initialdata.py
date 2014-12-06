# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def default_publications(apps, schema_editor):
    Publication = apps.get_model('newsletter', 'Publication')
    Publication(slug='poi', name='Points of Interest', publication_day='6',
                mime_types='application/pdf', is_private=True).save()


class Migration(migrations.Migration):

    dependencies = [
        ('newsletter', '0001_initial')
    ]

    operations = [
        migrations.RunPython(default_publications),
    ]
