from django.core.cache import InvalidCacheBackendError, caches
from django.core.cache.utils import make_template_fragment_key
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import UploadedFile
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver

from ..utils.storages import (
    decrypt_s3_file,
    delete_s3_file,
    encrypt_s3_file,
    is_s3_encrypted,
    is_s3_file,
    is_s3_file_public,
    set_s3_file_acl,
)
from .models import Attachment, Resource, ResourceFeed, Tag, get_attachment_filename, get_feed_artwork_filename


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


def prefix_slug(instance, tag_ids=None):
    if tag_ids:
        tags = [Tag.objects.get(id=pk) for pk in tag_ids]
    else:
        tags = Tag.objects.all()
    for tag in tags:
        if tag.slug_prefix:
            prefix = tag.slug_prefix
            if "%" in tag.slug_prefix:
                prefix = instance.published.strftime(tag.slug_prefix)
            if not instance.slug.startswith(prefix):
                instance.slug = prefix + instance.slug


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
    for attachment in instance.attachments.all():
        if is_s3_file(attachment.file):
            was_private = getattr(instance, "was_private", None)
            if was_private is not None and was_private != instance.is_private:
                if is_s3_encrypted(attachment.file):
                    if not instance.is_private:
                        decrypt_s3_file(attachment.file)
                else:
                    if instance.is_private:
                        encrypt_s3_file(attachment.file)
                if is_s3_file_public(attachment.file):
                    if instance.is_private:
                        set_s3_file_acl(attachment.file, "private")
                else:
                    if not instance.is_private:
                        set_s3_file_acl(attachment.file, "public-read")
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
        instance.was_private = sender.objects.get(id=instance.id).is_private
    except ObjectDoesNotExist:
        instance.was_private = not instance.is_private
    try:
        instance.was_featured = sender.objects.get(id=instance.id).is_featured
    except ObjectDoesNotExist:
        instance.was_featured = not instance.is_featured
    try:
        if instance.is_published and not sender.objects.get(id=instance.id).is_published:
            prefix_slug(instance)
    except ObjectDoesNotExist:
        pass


@receiver(m2m_changed, sender=Resource.tags.through)
def resource_m2m_changed(sender, instance, action, pk_set, **kwargs):
    _ = sender

    if action != "pre_add" or not instance.published:
        return

    # Make sure we only alter brand new slugs
    if (instance.modified - instance.created).seconds > 15:
        return

    old_slug = instance.slug
    prefix_slug(instance, pk_set)
    if old_slug != instance.slug:
        instance.save()


@receiver(pre_save, sender=Attachment)
def attachment_pre_save(sender, instance, **kwargs):
    _ = sender
    if kwargs.get("raw"):
        return
    if isinstance(instance.file.file, UploadedFile):
        # Work to be done when a new file is uploaded
        instance.file_new = True
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
        if not instance.is_private:
            instance.file.storage.save_cleartext(get_attachment_filename(instance, instance.file.name))


@receiver(post_save, sender=Attachment)
def attachment_post_save(sender, instance, **kwargs):
    _ = sender
    if kwargs.get("raw"):
        return
    if getattr(instance, "file_new", False) and not instance.resource.is_private and is_s3_file(instance.file):
        set_s3_file_acl(instance.file, "public-read")


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
        instance.artwork_new = True
        # Delete any old file so the path is clear for the new file.
        # There is a risk that the ensuing save() will fail, which will
        # leave the file missing.
        if old_artwork:
            delete_file(old_artwork)
        instance.artwork.storage.save_cleartext(get_feed_artwork_filename(instance, instance.artwork.name))


@receiver(post_save, sender=ResourceFeed)
def feed_post_save(sender, instance, **kwargs):
    _ = sender
    if kwargs.get("raw"):
        return
    if instance.artwork and is_s3_file(instance.artwork):
        if getattr(instance, "artwork_new", False):
            if not is_s3_file_public(instance.artwork):
                set_s3_file_acl(instance.artwork, "public-read")


@receiver(post_delete, sender=ResourceFeed)
def feed_post_delete(sender, instance, **kwargs):
    _ = sender
    if instance.artwork:
        delete_file(instance.artwork)
