from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ExtendedSite


@receiver(post_save, sender=ExtendedSite)
def extendedsite_post_save(**kwargs):
    Site.objects.clear_cache()
