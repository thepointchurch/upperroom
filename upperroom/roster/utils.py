import logging
from datetime import date, timedelta

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from ..utils.tasks import send_email
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

    site_name = get_current_site(None).name

    for person, roles in role_map.items():
        message = mail.EmailMessage(
            subject=_("%(site)s Roster Notification") % {"site": site_name},
            body=get_template("roster/reminder.txt").render(
                {"person": person, "date": notification_date, "role_list": roles}
            ),
            from_email=settings.ROSTER_EMAIL,
            to=[person.find_email],
        )
        if test:
            with mail.get_connection(backend="django.core.mail.backends.console.EmailBackend") as connection:
                connection.send_messages(message)
        else:
            send_email.enqueue(message)
