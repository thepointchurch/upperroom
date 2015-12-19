from django.apps import apps
from django.db.models.signals import post_migrate

from resources.models import Tag


def add_tags(sender, **kwargs):
    tag, created = Tag.objects.get_or_create(slug='about')
    if created:
        tag.name = 'About Us'
        tag.description = 'Aquaint yourself with The Point and what we belive.'
        tag.resources_per_page = None
        tag.reverse_order = False
        tag.is_exclusive = True
        tag.priority = 10
        tag.show_date = False
        tag.save()

post_migrate.connect(add_tags, sender=apps.get_app_config('resources'))
