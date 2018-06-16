from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import UploadedFile
from django.db.models.signals import post_migrate, post_delete, pre_save, post_save
from django.dispatch import receiver
from django.utils.translation import ugettext as _
from storages.backends.s3boto3 import S3Boto3StorageFile

from .models import Attachment, Resource, ResourceFeed, Tag


def is_s3_file_public(file_object):
    for grant in file_object.file.obj.Acl().grants:
        if grant['Permission'] == 'READ' and \
                grant['Grantee']['URI'] == 'http://acs.amazonaws.com/groups/global/AllUsers':
            return True
    return False


def set_s3_file_acl(file_object, acl):
    file_object.file.obj.Acl().put(ACL=acl)


def delete_file(file_object):
    if hasattr(file_object, 'storage'):
        try:
            if hasattr(file_object, 'path'):
                file_object.storage.delete(file_object.path)
        except NotImplementedError:
            # S3 storage uses `name`, not `path`
            file_object.storage.delete(file_object.name)


@receiver(post_save, sender=Resource)
def resource_post_save(sender, instance, **kwargs):
    for attachment in instance.attachments.all():
        if isinstance(attachment.file.file, S3Boto3StorageFile):
            was_private = getattr(instance, 'was_private', None)
            if was_private is not None and was_private != instance.is_private:
                if is_s3_file_public(attachment.file):
                    if instance.is_private:
                        set_s3_file_acl(attachment.file, 'private')
                else:
                    if not instance.is_private:
                        set_s3_file_acl(attachment.file, 'public-read')


@receiver(pre_save, sender=Resource)
def resource_pre_save(sender, instance, **kwargs):
    try:
        instance.was_private = sender.objects.get(id=instance.id).is_private
    except ObjectDoesNotExist:
        instance.was_private = not instance.is_private


@receiver(pre_save, sender=Attachment)
def attachment_pre_save(sender, instance, **kwargs):
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


@receiver(post_save, sender=Attachment)
def attachment_post_save(sender, instance, **kwargs):
    if getattr(instance, 'file_new', False) and not instance.resource.is_private:
        set_s3_file_acl(instance.file, 'public-read')


@receiver(post_delete, sender=Attachment)
def attachment_post_delete(sender, instance, **kwargs):
    if instance.file:
        delete_file(instance.file)


@receiver(pre_save, sender=ResourceFeed)
def feed_pre_save(sender, instance, **kwargs):
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


@receiver(post_save, sender=ResourceFeed)
def feed_post_save(sender, instance, **kwargs):
    if instance.artwork and isinstance(instance.artwork.file, S3Boto3StorageFile):
        if getattr(instance, 'artwork_new', False):
            if not is_s3_file_public(instance.artwork):
                set_s3_file_acl(instance.artwork, 'public-read')


@receiver(post_delete, sender=ResourceFeed)
def feed_post_delete(sender, instance, **kwargs):
    if instance.artwork:
        delete_file(instance.artwork)


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
