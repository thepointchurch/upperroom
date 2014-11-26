import csv
import sys
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from library.models import Book

class Command(BaseCommand):
    args = '< books.csv'
    help = '''Import books into the library through a CSV file on stdin.'''

    option_list = BaseCommand.option_list + (
        make_option('--refresh',
            action='store_true',
            dest='refresh',
            default=True,
            help='Delete all books before importing the supplied set'),
        make_option('--no-refresh',
            action='store_false',
            dest='refresh',
            help='Keep existing books when importing the supplied set'),
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

            book = Book(title=line[0], subtitle=line[1], description=line[2], type=line[3], author=line[4], isbn=line[5], location=line[6])
            book.save()
