from datetime import date, datetime
from optparse import make_option

from django.core import mail
from django.core.management.base import BaseCommand, CommandError
from django.template import Context
from django.template.loader import get_template

from roster.models import Role, next_meeting_date


class Command(BaseCommand):
    help = '''Send notification emails for a coming meeting.'''

    option_list = BaseCommand.option_list + (
        make_option('-d', '--date',
                    dest='date',
                    default=next_meeting_date(),
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

        roles = Role.objects.filter(meeting__date=d).exclude(person__isnull=True)
        role_map = {}
        for role in roles:
            if not role.person.find_email():
                continue

            if role.person not in role_map.keys():
                role_map[role.person] = []

            role_map[role.person].append(role)

        backend = None
        if options['test']:
            backend = 'django.core.mail.backends.console.EmailBackend'

        connection = mail.get_connection(backend)
        connection.open()

        messages = []

        for person, roles in role_map.items():
            role_string = ''
            for counter, role in enumerate(roles):
                if len(roles) > 1 and counter >= 1:
                    if len(roles) > 2:
                        role_string += ','
                    if counter + 1 == len(roles):
                        role_string += ' and '
                    else:
                        role_string += ' '
                role_string += role.role.verb
                if role.location:
                    role_string += ' at ' + str(role.location)

            messages.append(mail.EmailMessage(
                'The Point Roster Notification',
                get_template('roster/reminder.txt').render(Context({
                    'person': person,
                    'date': d,
                    'role_list': roles,
                    'role_string': role_string,
                })),
                'webmaster@thepoint.org.au',
                [person.find_email()], connection=connection))

        connection.send_messages(messages)
        connection.close()
