import sys
from datetime import date

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from weasyprint import HTML

from ...models import Meeting


def this_year():
    return date.today().year


class Command(BaseCommand):
    help = "Generate a PDF version of the roster."

    def add_arguments(self, parser):
        parser.add_argument(
            "-y", "--year", dest="year", type=int, default=this_year(), help=_("The year to generate the roster for")
        )
        parser.add_argument(
            "-w",
            "--week-day",
            dest="week_day",
            type=int,
            default=1,  # Sunday
            help=_("The week day to generate the roster for"),
        )
        parser.add_argument("-o", "--output", dest="output", help=_("File to write the PDF to"))

    def handle(self, *args, **options):
        year = options["year"]
        week_day = options["week_day"]
        output = options["output"]

        html = get_template("roster/pdf.html").render(
            {
                "site_name": get_current_site(None).name,
                "contact_email": settings.ROSTER_EMAIL,
                "year": year,
                "meeting_list": Meeting.objects.all().filter(date__year=year, date__week_day=week_day),
            }
        )
        pdf_data = HTML(string=html, encoding="utf-8").write_pdf()

        if output:
            with open(output, "wb") as pdf:
                pdf.write(pdf_data)
        else:
            sys.stdout.buffer.write(pdf_data)
