import csv
import sys
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from library.models import Book


class Command(BaseCommand):
    args = '< books.csv'
    help = '''Import books into the library through a CSV file on stdin.'''

    option_list = BaseCommand.option_list + (
        make_option('--refresh',
                    action='store_true',
                    dest='refresh',
                    default=True,
                    help='Delete all books before importing'),
        make_option('--no-refresh',
                    action='store_false',
                    dest='refresh',
                    help='Keep existing books when importing'),
        )

    def handle(self, *args, **options):
        if options['refresh']:
            Book.objects.all().delete()

        for line in csv.reader(sys.stdin):
            if len(line) < 7:
                raise CommandError('Badly formatted book: ' % line)

            if line[0] == '':
                self.stderr.write('WARNING: Book has no title: ' % line)
                continue

            book = Book(title=line[0].strip().replace('', '\n'),
                        subtitle=line[1].strip().replace('', '\n'),
                        description=line[2].strip().replace('', '\n'),
                        type=line[3].strip().replace('', '\n'),
                        author=line[4].strip().replace('', '\n'),
                        isbn=line[5].strip().replace('', '\n'),
                        location=line[6].strip().replace('', '\n'))
            book.save()
