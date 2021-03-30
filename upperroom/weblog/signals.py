from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import UploadedFile
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from ..resources.signals import delete_file
from .models import Attachment


@receiver(pre_save, sender=Attachment)
def attachment_pre_save(sender, instance, **kwargs):
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


@receiver(post_delete, sender=Attachment)
def attachment_post_delete(sender, instance, **kwargs):
    _ = sender
    if instance.file:
        delete_file(instance.file)
