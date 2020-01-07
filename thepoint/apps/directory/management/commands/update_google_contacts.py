import json
import logging
import os.path

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from ...models import Person


logger = logging.getLogger()
logger.setLevel(logging.WARNING)


class Contact(object):
    def __init__(self, id, given_name, surname, suffix=None, email=None, groups=None):
        self.id = id
        self.given_name = given_name
        self.surname = surname
        self.suffix = suffix
        self.email = email
        if not groups:
            self.groups = set()
        else:
            self.groups = groups

    def __repr__(self):
        return 'Contact(%r, %r, %r, %r, %r, %r)' % (self.id,
                                                    self.given_name,
                                                    self.surname,
                                                    self.suffix,
                                                    self.email,
                                                    self.groups)

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return False
        else:
            return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def add_group(self, group_id):
        self.groups.add(group_id)


class GooglePeopleService(object):
    class MemoryCache(object):
        _CACHE = {}

        def get(self, url):
            return self._CACHE.get(url)

        def set(self, url, content):
            self._CACHE[url] = content

    def __init__(self, secrets_file, credentials=None, dry_run=False):
        self.dry_run = dry_run

        if credentials and os.path.isfile(credentials):
            with open(credentials, 'r') as f:
                creds_data = json.load(f)
            creds = Credentials(creds_data['token'])
        else:
            flow = InstalledAppFlow.from_client_secrets_file(secrets_file,
                                                             scopes=['https://www.googleapis.com/auth/contacts'])
            flow.run_console()
            creds = flow.credentials

            if credentials:
                creds_data = {
                    'token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_uri': creds.token_uri,
                    'client_id': creds.client_id,
                    'client_secret': creds.client_secret,
                    'scopes': creds.scopes
                }
                with open(credentials, 'w') as f:
                    json.dump(creds_data, f)

        self.service = build('people', 'v1', credentials=creds, cache=GooglePeopleService.MemoryCache())

    def get_groups(self):
        groups = dict()

        for group in self.service.contactGroups().list().execute().get('contactGroups', []):
            if group['groupType'] == 'USER_CONTACT_GROUP':
                groups[self.service.contactGroups().get(resourceName=group['resourceName'])
                       .execute()['resourceName']] = group

        return groups

    def get_group_members(self, resource_name, max_members=200):
        if resource_name is None:  # needed during dry-runs
            return []
        else:
            return self.service.contactGroups().get(resourceName=resource_name,
                                                    maxMembers=max_members).execute()['memberResourceNames']

    def get_contacts(self):
        contacts = dict()
        next_page = 0

        while next_page is not None:
            x = self.service.people().connections().list(resourceName='people/me',
                                                         pageToken=next_page if next_page else None,
                                                         personFields='names,emailAddresses,memberships,userDefined'
                                                         ).execute()
            for person in x.get('connections', []):
                directory_id, given_name, surname, suffix, email = None, None, None, None, None

                for d in person.get('userDefined', []):
                    if d['key'] == 'directory_id':
                        directory_id = d['value']

                names = person.get('names', [])
                if names:
                    given_name = names[0].get('givenName')
                    surname = names[0].get('familyName')
                    s = names[0].get('honorificSuffix')
                    if s:
                        suffix = s

                for address in person.get('emailAddresses', []):
                    if address['metadata'].get('primary', False):
                        email = address['value']
                        break

                p = Contact(directory_id, given_name, surname, suffix, email)
                p.google_id = person['resourceName']
                p.google_etag = person['etag']

                for group in person.get('memberships', []):
                    if 'contactGroupMembership' in group:
                        gid = group['contactGroupMembership']['contactGroupId']
                        if gid not in ['myContacts', 'starred']:
                            p.add_group(gid)

                contacts[p.id] = p

            next_page = x.get('nextPageToken')

        return contacts

    def create_group(self, name):
        if self.dry_run:
            print('create_group(%r)' % name)  # must return something
            return {'resourceName': None}
        else:
            return self.service.contactGroups().create(body={'contactGroup': {'name': name}}).execute()

    def get_or_create_group(self, name):
        for k, v in self.get_groups().items():
            if v['name'] == name:
                return v
        return self.create_group(name)

    def update_group_membership(self, resource_name, to_add=set(), to_remove=set()):
        if self.dry_run:
            print('update_group_membership(%r, %r, %r)' % (resource_name, to_add, to_remove))
        else:
            self.service.contactGroups().members().modify(resourceName=resource_name, body={
                'resourceNamesToRemove': list(to_remove),
                'resourceNamesToAdd': list(to_add),
            }).execute()

    def create_contact(self, contact):
        if self.dry_run:
            print('create_contact(%r)' % contact)
        else:
            result = self.service.people().createContact(body={
                'names': [{
                    'givenName': contact.given_name,
                    'familyName': contact.surname,
                    'honorificSuffix': contact.suffix,
                }],
                'emailAddresses': [{
                    'metadata': {'primary': True},
                    'value': contact.email,
                }],
                'userDefined': [{
                    'key': 'directory_id',
                    'value': str(contact.id),
                }]}).execute()
            contact.google_id = result['resourceName']

    def update_contact(self, contact):
        if self.dry_run:
            print('update_contact(%r)' % contact)
        else:
            self.service.people().updateContact(resourceName=contact.google_id, body={
                'etag': contact.google_etag,
                'names': [{
                    'givenName': contact.given_name,
                    'familyName': contact.surname,
                    'honorificSuffix': contact.suffix,
                }],
                'emailAddresses': [{
                    'metadata': {'primary': True},
                    'value': contact.email,
                }],
            }, updatePersonFields='names,emailAddresses').execute()


class Command(BaseCommand):
    help = _('Update contacts in Gmail from the directory.')

    def add_arguments(self, parser):
        parser.add_argument('--secrets',
                            dest='secrets',
                            required=True,
                            help=_('The OAuth2 client secrets file'))
        parser.add_argument('--credentials',
                            dest='credentials',
                            help=_('Optional location to store OAuth2 credentials between runs'))
        parser.add_argument('--dry-run',
                            dest='dry_run',
                            action='store_true',
                            help=_("Don't take any action, only show what would be done"))

    def handle(self, *args, **options):
        people = {}
        for p in Person.current_objects.filter(is_member=True):
            e = p.find_email()
            if e:
                c = Contact(str(p.id), p.name, p.surname, p.suffix if p.suffix else None, e)
                c.obj = p
                people[c.id] = c
        directory_contacts = set(people.values())

        service = GooglePeopleService(secrets_file=options['secrets'],
                                      credentials=options['credentials'],
                                      dry_run=options['dry_run'])
        contacts = service.get_contacts()
        google_contacts = set(contacts.values())

        for a in sorted(list(directory_contacts.difference(google_contacts)), key=lambda x: x.id):
            service.create_contact(a)

        for a in directory_contacts.intersection(google_contacts):
            g = contacts[a.id]
            d = people[a.id]
            if g.given_name != d.given_name or g.surname != d.surname or g.suffix != d.suffix or g.email != d.email:
                g.given_name = d.given_name
                g.surname = d.surname
                g.suffix = d.suffix
                g.email = d.email
                service.update_contact(g)

        # Define the groups we want to synchronise
        groups = {
            'Members': lambda x: True,
            'Roster Participants': lambda x: x.roles.count() > 0,
        }

        for group_name, test_func in groups.items():
            group = service.get_or_create_group(group_name)
            google_members = set(service.get_group_members(group['resourceName']))
            current_members = set([contacts[person_id].google_id
                                   for person_id, person in people.items()
                                   if test_func(person.obj)])

            to_add = current_members.difference(google_members)
            to_remove = google_members.difference(current_members)

            if to_add or to_remove:
                service.update_group_membership(group['resourceName'], to_add, to_remove)
