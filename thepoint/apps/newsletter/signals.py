from django.apps import apps
from django.db.models.signals import post_migrate

from .models import Publication


def default_publications(sender, **kwargs):
    p, created = Publication.objects.get_or_create(slug='poi')
    if created:
        p.name = 'Points of Interest'
        p.publication_day = '6'
        p.mime_types = 'application/pdf'
        p.is_private = True
        p.save()


post_migrate.connect(default_publications,
                     sender=apps.get_app_config('newsletter'))
