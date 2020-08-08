from io import BytesIO

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db.models.signals import pre_save, post_save
from django.dispatch import Signal, receiver
from django.template.loader import get_template
from django.utils.translation import gettext as _
from PIL import Image

from .models import Family, get_family_photo_filename, get_family_thumbnail_filename
from ..resources.signals import delete_file


family_updated = Signal()


@receiver(family_updated)
def notify_on_fupdate(sender, instance, **kwargs):
    send_mail(_('%(site)s Directory Update') % {'site': get_current_site(None).name},
              get_template('directory/update_notify.txt').render({
                  'family': instance,
              }),
              settings.WEBMASTER_EMAIL,
              [settings.DIRECTORY_EMAIL],
              html_message=get_template('directory/update_notify.html')
              .render({
                  'family': instance,
              })
              )


@receiver(pre_save, sender=Family)
def family_pre_save(sender, instance, **kwargs):
    if kwargs.get('raw'):
        return

    try:
        old_instance = sender.objects.get(id=instance.id)
    except Family.DoesNotExist:
        return
    if old_instance.photo == instance.photo:
        return

    # Delete any old file so the path is clear for the new file.
    # There is a risk that the ensuing save() will fail, which will
    # leave the file missing.
    try:
        if old_instance.photo:
            delete_file(old_instance.photo)
    except ObjectDoesNotExist:
        pass
    try:
        if old_instance.photo_thumbnail:
            delete_file(old_instance.photo_thumbnail)
    except ObjectDoesNotExist:
        pass

    if instance.photo:
        image = Image.open(instance.photo).convert('RGB')

        image.thumbnail(getattr(settings, 'DIRECTORY_IMAGE_MAX', (1000, 1000)))

        f = BytesIO()
        image.save(f, 'JPEG')
        f.seek(0)
        instance.photo.save(get_family_photo_filename(instance, None), ContentFile(f.read()), save=False)
        f.close()

        image.thumbnail(getattr(settings, 'DIRECTORY_THUMBNAIL_MAX', (240, 240)))

        f = BytesIO()
        image.save(f, 'JPEG')
        f.seek(0)
        instance.photo_thumbnail.save(get_family_thumbnail_filename(instance, None), ContentFile(f.read()), save=False)
        f.close()
    else:
        instance.photo_thumbnail = None


@receiver(post_save, sender=User)
def add_user_to_member_group(sender, instance, created, **kwargs):
    if created:
        try:
            instance.groups.add(Group.objects.get(name='Member'))
        except Group.DoesNotExist:
            pass
