from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import Signal, receiver
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _


family_updated = Signal(providing_args=['instance'])


@receiver(family_updated)
def notify_on_fupdate(sender, instance, **kwargs):
    send_mail(_('%(site)s Directory Update') % {'site': settings.SITE_NAME},
              get_template('directory/update_notify.txt').render(Context({
                  'family': instance,
              })),
              settings.DEFAULT_FROM_EMAIL,
              [settings.DIRECTORY_NOTIFY_EMAIL],
              html_message=get_template('directory/update_notify.html')
              .render(Context({
                  'family': instance,
              }))
              )
