from datetime import date
from io import BytesIO

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from django.utils.dates import MONTHS
from django.utils.translation import ugettext_lazy as _
from weasyprint import HTML

from ...models import Family, Person
from ...views import directory_file_name


def this_year():
    return date.today().year


def this_month():
    return date.today().month


class Command(BaseCommand):
    help = 'Generate a PDF version of the directory.'

    def add_arguments(self, parser):
        parser.add_argument('-y', '--year',
                            dest='year',
                            type=int,
                            default=this_year(),
                            help=_('The year to generate the directory for'))
        parser.add_argument('-m', '--month',
                            dest='month',
                            type=int,
                            default=this_month(),
                            help=_('The month to generate the directory for'))
        parser.add_argument('-o', '--output',
                            dest='output',
                            help=_('Local file to write the PDF to'))

    def handle(self, *args, **options):
        year = options['year']
        month = MONTHS[options['month']]
        output = options['output']

        html = get_template('directory/print.html').render({
            'site_name': get_current_site(None).name,
            'contact_email': settings.DIRECTORY_EMAIL,
            'month': month,
            'year': year,
            'families': Family.current_objects.all(),
            'birthdays': Person.current_objects.all().exclude(birthday__isnull=True),
            'anniversaries': (Family.current_objects
                              .filter(anniversary__isnull=False)
                              .filter(husband__isnull=False)
                              .filter(wife__isnull=False)
                              ),
        })
        pdf_data = HTML(string=html, encoding='utf-8').write_pdf()

        if output:
            with open(output, 'wb') as f:
                f.write(pdf_data)
        else:
            f = BytesIO()
            f.write(pdf_data)
            if default_storage.exists(directory_file_name):
                default_storage.delete(directory_file_name)
            default_storage.save(directory_file_name, f)
            f.close()
