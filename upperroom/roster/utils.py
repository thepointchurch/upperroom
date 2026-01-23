import logging
from datetime import date, timedelta

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from .models import Role

logger = logging.getLogger(__name__)


def _get_role_map(roles):
    role_map = {}

    for role in roles:
        for person in role.people.all():
            if not person.find_email:
                continue

            if person not in role_map:
                role_map[person] = []

            role_map[person].append(role)

    return role_map


def send_roster_emails(notification_date=None, alert_interval=3, test=False):
    if not notification_date:
        notification_date = date.today() + timedelta(days=alert_interval)

    role_map = _get_role_map(Role.objects.filter(meeting__date=notification_date).exclude(people__isnull=True))

    backend = None
    if test:
        backend = "django.core.mail.backends.console.EmailBackend"

    connection = mail.get_connection(backend=backend)
    connection.open()

    messages = []

    site_name = get_current_site(None).name

    for person, roles in role_map.items():
        messages.append(
            mail.EmailMessage(
                subject=_("%(site)s Roster Notification") % {"site": site_name},
                body=get_template("roster/reminder.txt").render(
                    {"person": person, "date": notification_date, "role_list": roles}
                ),
                from_email=settings.ROSTER_EMAIL,
                to=[person.find_email],
                connection=connection,
            )
        )

    connection.send_messages(messages)
    connection.close()

    if not test:
        for message in messages:
            for recipient in message.to:
                logger.info("Sent mail to <%s>: %s", recipient, message.subject)
