from django.apps import apps
from django.db.models.signals import post_migrate

from newsletter.models import Publication


def default_publications(sender, **kwargs):
    Publication(slug='poi', name='Points of Interest', publication_day='6',
                mime_types='application/pdf', is_private=True).save()

post_migrate.connect(default_publications,
                     sender=apps.get_app_config('newsletter'))
