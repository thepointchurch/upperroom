# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def default_locations(apps, schema_editor):
    Location = apps.get_model('roster', 'Location')
    Location(name='Gold Coast').save()
    Location(name='Maryborough').save()
    Location(name='Morayfield').save()
    Location(name='Sunshine Coast').save()
    Location(name='Warwick').save()
    Location(name='Wynnum').save()


def default_roletypes(apps, schema_editor):
    RoleType = apps.get_model('roster', 'RoleType')
    RoleType(name='Lesson',
             verb='bring the lesson', order=10).save()
    RoleType(name="Kid's Time",
             verb="lead Kid's Time", order=20).save()
    RoleType(name='Focus Theme',
             verb='lead the Focus Theme', order=30).save()
    RoleType(name='Singing',
             verb='lead the singing', order=40).save()
    RoleType(name='Communion',
             verb='lead Communion', order=50).save()
    RoleType(name='Assisting Communion',
             verb='assist with Communion', order=60).save()
    RoleType(name='News Sharing',
             verb='lead the announcements', order=70).save()
    RoleType(name='Benediction',
             verb='offer the benediction', order=80).save()
    RoleType(name='Guest Teaching',
             verb='be the guest teacher', order=90).save()


class Migration(migrations.Migration):

    dependencies = [
        ('roster', '0001_initial')
    ]

    operations = [
        migrations.RunPython(default_locations),
        migrations.RunPython(default_roletypes),
    ]
