from django.apps import apps
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext as _

from resources.models import Tag


def add_tags(sender, **kwargs):
    tag, created = Tag.objects.get_or_create(slug='about')
    if created:
        tag.name = _('About Us')
        tag.description = _('Aquaint yourself with The Point and what we belive.')
        tag.resources_per_page = None
        tag.reverse_order = True
        tag.is_exclusive = True
        tag.priority = 10
        tag.show_date = False
        tag.save()


post_migrate.connect(add_tags, sender=apps.get_app_config('resources'))
