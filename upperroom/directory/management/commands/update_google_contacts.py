# pylint: disable=no-member,too-many-arguments,too-many-instance-attributes,too-many-locals

import json
import logging
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from google.oauth2.credentials import Credentials  # pylint: disable=import-error
from google_auth_oauthlib.flow import InstalledAppFlow  # pylint: disable=import-error
from googleapiclient.discovery import build  # pylint: disable=import-error

from ...models import Person

logger = logging.getLogger()
logger.setLevel(logging.WARNING)


class Contact:
    def __init__(self, contact_id, given_name, surname, suffix=None, email=None, groups=None):
        self.id = contact_id  # pylint: disable=invalid-name
        self.given_name = given_name
        self.surname = surname
        self.suffix = suffix
        self.email = email
        if not groups:
            self.groups = set()
        else:
            self.groups = groups

        self.google_id = None
        self.google_etag = None
        self.obj = None

    def __repr__(self):
        return (
            f"Contact({self.id!r}, {self.given_name!r}, {self.surname!r}, {self.suffix!r}, "
            f"{self.email!r}, {self.groups}!r)"
        )

    def __eq__(self, other):
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def add_group(self, group_id):
        self.groups.add(group_id)


class GooglePeopleService:
    class MemoryCache:
        _CACHE = {}

        def get(self, url):
            return self._CACHE.get(url)

        def set(self, url, content):
            self._CACHE[url] = content

    def __init__(self, secrets_file, credentials=None, dry_run=False):
        self.dry_run = dry_run

        if credentials and Path(credentials).is_file():
            with open(credentials, "r", encoding="utf-8") as creds_file:
                creds_data = json.load(creds_file)
            creds = Credentials(creds_data["token"])
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                secrets_file, scopes=["https://www.googleapis.com/auth/contacts"]
            )
            flow.run_console()
            creds = flow.credentials

            if credentials:
                creds_data = {
                    "token": creds.token,
                    "refresh_token": creds.refresh_token,
                    "token_uri": creds.token_uri,
                    "client_id": creds.client_id,
                    "client_secret": creds.client_secret,
                    "scopes": creds.scopes,
                }
                with open(credentials, "w", encoding="utf-8") as creds_file:
                    json.dump(creds_data, creds_file)

        self.service = build("people", "v1", credentials=creds, cache=GooglePeopleService.MemoryCache())

    def get_groups(self):
        groups = {}

        for group in self.service.contactGroups().list().execute().get("contactGroups", []):
            if group["groupType"] == "USER_CONTACT_GROUP":
                groups[
                    self.service.contactGroups().get(resourceName=group["resourceName"]).execute()["resourceName"]
                ] = group

        return groups

    def get_group_members(self, resource_name, max_members=200):
        if resource_name is None:  # needed during dry-runs
            return []
        return (
            self.service.contactGroups()
            .get(resourceName=resource_name, maxMembers=max_members)
            .execute()["memberResourceNames"]
        )

    def get_contacts(self):  # NOQA: C901
        contacts = {}
        next_page = 0

        while next_page is not None:
            cmd = (
                self.service.people()
                .connections()
                .list(
                    resourceName="people/me",
                    pageToken=next_page if next_page else None,
                    personFields="names,emailAddresses,memberships,userDefined",
                )
                .execute()
            )
            for person in cmd.get("connections", []):
                directory_id, given_name, surname, suffix, email = None, None, None, None, None

                for user_defined in person.get("userDefined", []):
                    if user_defined["key"] == "directory_id":
                        directory_id = user_defined["value"]

                names = person.get("names", [])
                if names:
                    given_name = names[0].get("givenName")
                    surname = names[0].get("familyName")
                    suffix_ = names[0].get("honorificSuffix")
                    if suffix_:
                        suffix = suffix_

                for address in person.get("emailAddresses", []):
                    if address["metadata"].get("primary", False):
                        email = address["value"]
                        break

                contact = Contact(directory_id, given_name, surname, suffix, email)
                contact.google_id = person["resourceName"]
                contact.google_etag = person["etag"]

                for group in person.get("memberships", []):
                    if "contactGroupMembership" in group:
                        gid = group["contactGroupMembership"]["contactGroupId"]
                        if gid not in ["myContacts", "starred"]:
                            contact.add_group(gid)

                contacts[contact.id] = contact

            next_page = cmd.get("nextPageToken")

        return contacts

    def create_group(self, name):
        if self.dry_run:
            print(f"create_group({name!r})")  # must return something
            return {"resourceName": None}
        return self.service.contactGroups().create(body={"contactGroup": {"name": name}}).execute()

    def get_or_create_group(self, name):
        for value in self.get_groups().values():
            if value["name"] == name:
                return value
        return self.create_group(name)

    def update_group_membership(self, resource_name, to_add, to_remove):
        if self.dry_run:
            print(f"update_group_membership({resource_name!r}, {to_add!r}, {to_remove!r})")
        else:
            self.service.contactGroups().members().modify(
                resourceName=resource_name,
                body={"resourceNamesToRemove": list(to_remove), "resourceNamesToAdd": list(to_add)},
            ).execute()

    def create_contact(self, contact):
        if self.dry_run:
            print(f"create_contact({contact!r})")
        else:
            result = (
                self.service.people()
                .createContact(
                    body={
                        "names": [
                            {
                                "givenName": contact.given_name,
                                "familyName": contact.surname,
                                "honorificSuffix": contact.suffix,
                            }
                        ],
                        "emailAddresses": [{"metadata": {"primary": True}, "value": contact.email}],
                        "userDefined": [{"key": "directory_id", "value": str(contact.id)}],
                    }
                )
                .execute()
            )
            contact.google_id = result["resourceName"]

    def update_contact(self, contact):
        if self.dry_run:
            print(f"update_contact({contact!r})")
        else:
            self.service.people().updateContact(
                resourceName=contact.google_id,
                body={
                    "etag": contact.google_etag,
                    "names": [
                        {
                            "givenName": contact.given_name,
                            "familyName": contact.surname,
                            "honorificSuffix": contact.suffix,
                        }
                    ],
                    "emailAddresses": [{"metadata": {"primary": True}, "value": contact.email}],
                },
                updatePersonFields="names,emailAddresses",
            ).execute()


class Command(BaseCommand):
    help = _("Update contacts in Gmail from the directory.")

    def add_arguments(self, parser):
        parser.add_argument("--secrets", dest="secrets", required=True, help=_("The OAuth2 client secrets file"))
        parser.add_argument(
            "--credentials", dest="credentials", help=_("Optional location to store OAuth2 credentials between runs")
        )
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help=_("Don't take any action, only show what would be done"),
        )

    def handle(self, *args, **options):
        people = {}
        for person in Person.current_objects.filter(is_member=True):
            email = person.find_email
            if email:
                contact = Contact(
                    str(person.id), person.name, person.surname, person.suffix if person.suffix else None, email
                )
                contact.obj = person
                people[contact.id] = contact
        directory_contacts = set(people.values())

        service = GooglePeopleService(
            secrets_file=options["secrets"], credentials=options["credentials"], dry_run=options["dry_run"]
        )
        contacts = service.get_contacts()
        google_contacts = set(contacts.values())

        for contact in sorted(list(directory_contacts.difference(google_contacts)), key=lambda x: x.id):
            service.create_contact(contact)

        for contact in directory_contacts.intersection(google_contacts):
            google_contact = contacts[contact.id]
            django_contact = people[contact.id]
            if (
                google_contact.given_name != django_contact.given_name
                or google_contact.surname != django_contact.surname
                or google_contact.suffix != django_contact.suffix
                or google_contact.email != django_contact.email
            ):
                google_contact.given_name = django_contact.given_name
                google_contact.surname = django_contact.surname
                google_contact.suffix = django_contact.suffix
                google_contact.email = django_contact.email
                service.update_contact(google_contact)

        # Define the groups we want to synchronise
        groups = {
            "Members": lambda x: True,
            "Roster Participants": lambda x: x.roles.count() > 0,
        }

        for group_name, test_func in groups.items():
            group = service.get_or_create_group(group_name)
            google_members = set(service.get_group_members(group["resourceName"]))
            current_members = {
                contacts[person_id].google_id for person_id, person in people.items() if test_func(person.obj)
            }

            to_add = current_members.difference(google_members)
            to_remove = google_members.difference(current_members)

            if to_add or to_remove:
                service.update_group_membership(group["resourceName"], to_add, to_remove)
