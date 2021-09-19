from django.core.cache import InvalidCacheBackendError, caches
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Splash


def clear_splash_cache(splash):
    try:
        cache = caches["template_fragments"]
    except InvalidCacheBackendError:
        cache = caches["default"]

    fragment_position = {Splash.POSITION_ABOVE: "above", Splash.POSITION_BELOW: "below"}[splash.position]
    fragment_name = f"splashes_{fragment_position}"
    cache.delete(make_template_fragment_key(fragment_name, [splash.url]))


@receiver(post_save, sender=Splash)
def splash_post_save(sender, instance, **kwargs):
    _ = sender
    clear_splash_cache(instance)


@receiver(post_delete, sender=Splash)
def splash_post_delete(sender, instance, **kwargs):
    _ = sender
    clear_splash_cache(instance)
