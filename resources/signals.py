from django.apps import apps
from resources.models import Tag
from django.db.models.signals import post_migrate


def add_tags(sender, **kwargs):
    tag, created = Tag.objects.get_or_create(slug='about')
    if created:
        tag.name = 'About'
        tag.resources_per_page = None
        tag.reverse_order = False
        tag.is_exclusive = True
        tag.save()

post_migrate.connect(add_tags, sender=apps.get_app_config('resources'))
