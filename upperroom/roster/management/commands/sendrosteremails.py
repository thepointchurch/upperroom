from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _

from ...models import Role

_ALERT_INTERVAL = 3  # days


def meeting_date():
    return date.today() + timedelta(days=_ALERT_INTERVAL)


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


class Command(BaseCommand):
    help = "Send notification emails for a coming meeting."

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--date", dest="date", default=meeting_date(), help=_("The meeting date to send notifications for")
        )
        parser.add_argument(
            "--test", action="store_true", dest="test", default=False, help=_("Send emails to the console only")
        )

    def handle(self, *args, **options):
        notification_date = options["date"]

        if not isinstance(notification_date, date):
            try:
                notification_date = datetime.strptime(notification_date, "%Y-%m-%d").date()
            except ValueError as exc:
                raise CommandError(f"Badly formatted date: {options['date']}") from exc

        role_map = _get_role_map(Role.objects.filter(meeting__date=notification_date).exclude(people__isnull=True))

        backend = None
        if options["test"]:
            backend = "django.core.mail.backends.console.EmailBackend"

        connection = mail.get_connection(backend)
        connection.open()

        messages = []

        site_name = get_current_site(None).name

        for person, roles in role_map.items():
            messages.append(
                mail.EmailMessage(
                    _("%(site)s Roster Notification") % {"site": site_name},
                    get_template("roster/reminder.txt").render(
                        {"person": person, "date": notification_date, "role_list": roles}
                    ),
                    settings.ROSTER_EMAIL,
                    [person.find_email],
                    connection=connection,
                )
            )

        connection.send_messages(messages)
        connection.close()

        if not options["test"]:
            for message in messages:
                for recipient in message.to:
                    self.stdout.write(f"Sent mail to <{recipient}>: {message.subject}")
