from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext_lazy as _

from ...utils import send_roster_emails


class Command(BaseCommand):
    help = "Send notification emails for a coming meeting."

    def add_arguments(self, parser):
        parser.add_argument(
            "-d", "--date", dest="date", default=None, help=_("The meeting date to send notifications for")
        )
        parser.add_argument(
            "--test", action="store_true", dest="test", default=False, help=_("Send emails to the console only")
        )

    def handle(self, *args, **options):
        notification_date = options["date"]

        if notification_date is not None and not isinstance(notification_date, date):
            try:
                notification_date = datetime.strptime(notification_date, "%Y-%m-%d").date()
            except ValueError as exc:
                raise CommandError(f"Badly formatted date: {options['date']}") from exc

        return send_roster_emails(notification_date, alert_interval=3, test=options["test"])
