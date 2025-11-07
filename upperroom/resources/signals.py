from django.core.cache import InvalidCacheBackendError, caches
from django.core.cache.utils import make_template_fragment_key
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import UploadedFile
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver

from ..utils.storages import delete_s3_file, is_s3_file
from .models import Attachment, Resource, ResourceFeed, Tag


def delete_file(file_object):
    if hasattr(file_object, "storage"):
        if is_s3_file(file_object):
            delete_s3_file(file_object)
        elif hasattr(file_object, "path"):
            file_object.storage.delete(file_object.path)


def clear_navbar_cache():
    try:
        cache = caches["template_fragments"]
    except InvalidCacheBackendError:
        cache = caches["default"]
    cache.delete(make_template_fragment_key("navbar_featured"))
    cache.delete(make_template_fragment_key("navbar_featured_private"))


@receiver(post_delete, sender=Resource)
def resource_post_delete(sender, instance, **kwargs):
    _ = sender
    if getattr(instance, "was_featured", None) or instance.is_featured:
        clear_navbar_cache()


@receiver(post_save, sender=Resource)
def resource_post_save(sender, instance, **kwargs):  # NOQA: C901
    _ = sender
    if kwargs.get("raw"):
        return
    if getattr(instance, "was_featured", None) or instance.is_featured:
        clear_navbar_cache()


@receiver(pre_delete, sender=Resource)
def resource_pre_delete(sender, instance, **kwargs):
    _ = sender
    try:
        instance.was_featured = sender.objects.get(id=instance.id).is_featured
    except ObjectDoesNotExist:
        instance.was_featured = not instance.is_featured


@receiver(pre_save, sender=Resource)
def resource_pre_save(sender, instance, **kwargs):
    _ = sender
    try:
        instance.was_featured = sender.objects.get(id=instance.id).is_featured
    except ObjectDoesNotExist:
        instance.was_featured = not instance.is_featured
    try:
        if instance.is_published and not sender.objects.get(id=instance.id).is_published:
            new_slug = instance.prefix_slug({t.id for t in Tag.objects.filter(resources__id=instance.id)})
            if new_slug:
                instance.slug = new_slug
    except ObjectDoesNotExist:
        pass


@receiver(m2m_changed, sender=Resource.tags.through)
def resource_m2m_changed(sender, instance, action, reverse, pk_set, **kwargs):
    _ = sender

    if action != "pre_add":
        return

    if reverse:
        resources = [Resource.objects.get(id=x) for x in pk_set]
        pk_set = {instance.id}
    else:
        resources = [instance]

    for resource in resources:
        # Make sure we only alter brand new slugs
        if (resource.modified - resource.created).seconds > 15:
            continue

        new_slug = resource.prefix_slug(pk_set)
        if new_slug and resource.slug != new_slug:
            resource.slug = new_slug
            resource.save()


@receiver(pre_save, sender=Attachment)
def attachment_pre_save(sender, instance, **kwargs):
    _ = sender
    if kwargs.get("raw"):
        return
    if isinstance(instance.file.file, UploadedFile):
        try:
            # Delete any old file so the path is clear for the new file.
            # There is a risk that the ensuing save() will fail, which will
            # leave the file missing.
            file_object = sender.objects.get(id=instance.id).file
            if file_object:
                delete_file(file_object)
        except ObjectDoesNotExist:
            pass
        instance.update_metadata()


@receiver(post_delete, sender=Attachment)
def attachment_post_delete(sender, instance, **kwargs):
    _ = sender
    if instance.file:
        delete_file(instance.file)


@receiver(pre_delete, sender=Tag)
def tag_pre_delete(sender, instance, **kwargs):
    _ = sender
    try:
        instance.was_featured = sender.objects.get(id=instance.id).is_featured
    except ObjectDoesNotExist:
        instance.was_featured = not instance.is_featured


@receiver(pre_save, sender=Tag)
def tag_pre_save(sender, instance, **kwargs):
    _ = sender
    try:
        instance.was_featured = sender.objects.get(id=instance.id).is_featured
    except ObjectDoesNotExist:
        instance.was_featured = not instance.is_featured


@receiver(post_delete, sender=Tag)
def tag_post_delete(sender, instance, **kwargs):
    _ = sender
    if getattr(instance, "was_featured", None) or instance.is_featured:
        clear_navbar_cache()


@receiver(post_save, sender=Tag)
def tag_post_save(sender, instance, **kwargs):
    _ = sender
    if getattr(instance, "was_featured", None) or instance.is_featured:
        clear_navbar_cache()


@receiver(pre_save, sender=ResourceFeed)
def feed_pre_save(sender, instance, **kwargs):
    _ = sender
    if kwargs.get("raw"):
        return
    try:
        old_artwork = sender.objects.get(id=instance.id).artwork
    except ObjectDoesNotExist:
        old_artwork = None

    # Artwork was deleted and not replaced
    if old_artwork and not instance.artwork:
        delete_file(old_artwork)

    # New artwork was uploaded
    if instance.artwork and isinstance(instance.artwork.file, UploadedFile):
        # Delete any old file so the path is clear for the new file.
        # There is a risk that the ensuing save() will fail, which will
        # leave the file missing.
        if old_artwork:
            delete_file(old_artwork)


@receiver(post_delete, sender=ResourceFeed)
def feed_post_delete(sender, instance, **kwargs):
    _ = sender
    if instance.artwork:
        delete_file(instance.artwork)
