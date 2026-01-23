from datetime import date

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from ...utils import generate_pdf


class Command(BaseCommand):
    help = "Generate a PDF version of the directory."

    def add_arguments(self, parser):
        parser.add_argument(
            "-y",
            "--year",
            dest="year",
            type=int,
            default=date.today().year,
            help=_("The year to generate the directory for"),
        )
        parser.add_argument(
            "-m",
            "--month",
            dest="month",
            type=int,
            default=date.today().month,
            help=_("The month to generate the directory for"),
        )
        parser.add_argument("-o", "--output", dest="output", help=_("Local file to write the PDF to"))
        parser.add_argument(
            "--compact", action="store_true", dest="compact", default=False, help=_("Generate the compact format")
        )

    def handle(self, *args, **options):
        return generate_pdf(options["compact"], options["output"], options["year"], options["month"])
