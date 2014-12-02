# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def setup_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    s = Site.objects.create(pk=1, domain='thepoint.org.au', name='thepoint')

    FlatPage = apps.get_model('flatpages', 'FlatPage')

    page, created = FlatPage.objects.get_or_create(url='/')
    if created:
        page.sites.add(s)
        page.title = "Welcome to The Point's website"
        page.template_name = 'pages/home.html'
        page.save()

    page, created = FlatPage.objects.get_or_create(url='/calendar/')
    if created:
        page.sites.add(s)
        page.title = 'Event Calendar'
        page.template_name = 'pages/calendar.html'
        page.registration_required = True
        page.save()

    page, created = FlatPage.objects.get_or_create(url='/contact/')
    if created:
        page.sites.add(s)
        page.title = 'Contact Details'
        page.template_name = 'pages/contact.html'
        page.save()

    page, created = FlatPage.objects.get_or_create(url='/copyright/')
    if created:
        page.sites.add(s)
        page.title = 'Copyright Notice'
        page.template_name = 'pages/copyright.html'
        page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('flatpages', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(setup_site)
    ]
