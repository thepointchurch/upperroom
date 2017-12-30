import csv
import sys

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _

from ....models import Book


class Command(BaseCommand):
    args = '< books.csv'
    help = _('Import books into the library through a CSV file on stdin.')

    def add_arguments(self, parser):
        parser.add_argument('--refresh',
                            action='store_true',
                            dest='refresh',
                            default=True,
                            help=_('Delete all books before importing'))
        parser.add_argument('--no-refresh',
                            action='store_false',
                            dest='refresh',
                            help=_('Keep existing books when importing'))

    def handle(self, *args, **options):
        if options['refresh']:
            Book.objects.all().delete()

        for line in csv.reader(sys.stdin):
            if len(line) < 7:
                raise CommandError(_('Badly formatted book: %(line)s') %
                                   {'line': line})

            if line[0] == '':
                self.stderr.write(_('WARNING: Book has no title: %(line)s') %
                                  {'line': line})
                continue

            book = Book(title=line[0].strip().replace('', '\n'),
                        subtitle=line[1].strip().replace('', '\n'),
                        description=line[2].strip().replace('', '\n'),
                        type=line[3].strip().replace('', '\n'),
                        author=line[4].strip().replace('', '\n'),
                        isbn=line[5].strip().replace('', '\n'),
                        location=line[6].strip().replace('', '\n'))
            book.save()
