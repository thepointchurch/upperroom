from datetime import date

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from ...models import Meeting


class Command(BaseCommand):
    help = _("Delete past meetings from the roster")

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help=_("Show a count of meetings to be deleted"),
        )

    def handle(self, *args, **options):
        meetings = Meeting.objects.filter(date__lt=date.today())
        if options["dry_run"]:
            self.stdout.write(_("%d meetings to be deleted") % meetings.count())
        else:
            count, __ = meetings.delete()
            self.stdout.write(_("Deleted %d meetings") % count)
