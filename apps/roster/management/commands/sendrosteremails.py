from datetime import date, datetime, timedelta
from optparse import make_option

from django.core import mail
from django.core.management.base import BaseCommand, CommandError
from django.template import Context
from django.template.loader import get_template

from roster.models import Role

_alert_interval = 3  # days


def meeting_date():
    return date.today() + timedelta(days=_alert_interval)


def _get_role_map(roles):
    role_map = {}

    for role in roles:
        for person in role.people.all():
            if not person.find_email():
                continue

            if person not in role_map.keys():
                role_map[person] = []

            role_map[person].append(role)

    return role_map


class Command(BaseCommand):
    help = '''Send notification emails for a coming meeting.'''

    option_list = BaseCommand.option_list + (
        make_option('-d', '--date',
                    dest='date',
                    default=meeting_date(),
                    help='The meeting date to send notifications for'),
        make_option('--test',
                    action='store_true',
                    dest='test',
                    default=False,
                    help='Send emails to the console only'),
        )

    def handle(self, *args, **options):
        d = options['date']

        if not isinstance(d, date):
            try:
                d = datetime.strptime(d, '%Y-%m-%d').date()
            except:
                raise CommandError('Badly formatted date: %s' %
                                   options['date'])

        role_map = _get_role_map(Role.objects.filter(meeting__date=d)
                                             .exclude(people__isnull=True))

        backend = None
        if options['test']:
            backend = 'django.core.mail.backends.console.EmailBackend'

        connection = mail.get_connection(backend)
        connection.open()

        messages = []

        for person, roles in role_map.items():
            messages.append(mail.EmailMessage(
                'The Point Roster Notification',
                get_template('roster/reminder.txt').render(Context({
                    'person': person,
                    'date': d,
                    'role_list': roles,
                })),
                'webmaster@thepoint.org.au',
                [person.find_email()], connection=connection))

        connection.send_messages(messages)
        connection.close()
