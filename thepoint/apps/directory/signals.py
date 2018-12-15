from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.dispatch import Signal, receiver
from django.template.loader import get_template
from django.utils.translation import ugettext as _


family_updated = Signal(providing_args=['instance'])


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
