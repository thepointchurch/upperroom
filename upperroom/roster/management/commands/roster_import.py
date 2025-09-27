import sys

import yaml
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Case, Q, Value, When
from django.db.models.functions import Concat
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _

from ....directory.models import Person
from ...models import Location, Meeting, Role, RoleType


class DoRollback(Exception):
    pass


# This loader ensures errors when there are duplicate keys in the import
class UniqueKeyLoader(yaml.SafeLoader):  # pylint: disable=too-many-ancestors
    def construct_mapping(self, node, deep=False):
        mapping = set()
        for key_node, __ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError(f"Duplicate {key!r} key found in YAML.")
            mapping.add(key)
        return super().construct_mapping(node, deep)


def load_data(import_file):
    if import_file:
        with open(import_file, "r", encoding="utf-8") as file_obj:
            return yaml.load(file_obj, Loader=UniqueKeyLoader)
    else:
        return yaml.load(sys.stdin, Loader=UniqueKeyLoader)


def lookup_person(full_name):
    # Since we can't use the fullname @property we have to emulate it here
    return Person.current_objects.annotate(
        full_name=Concat(
            "name",
            Value(" "),
            Case(
                When(
                    Q(surname_override__isnull=True) | Q(surname_override__exact=""),
                    then="family__name",
                ),
                default="surname_override",
            ),
            Case(
                When(Q(suffix__isnull=True) | Q(suffix__exact=""), then=Value("")),
                default=Concat(Value(" ("), "suffix", Value(")")),
            ),
        )
    ).get(full_name=full_name)


class Command(BaseCommand):
    """A sample roster import file:

    2026-01-01:
      Lesson:
        description: Love
        serving: Eric Idle
      Communion:
        serving: Graham Chapman
      Setup/Pack Up:
        serving:
        - Terry Gilliam
        - Michael Palin
      Guest Teaching:
        serving: John Cleese
        location: Torquay
    2026-01-08:
      Lesson:
        description: Judges
        serving: Bertie Wooster
      Communion:
        serving: Tuppy Glossop
      Setup/Pack Up:
        serving: Bingo Little
    """

    help = "Import meetings from YAML."

    def add_arguments(self, parser):
        parser.add_argument(
            "-f", "--file", dest="file", help=_("The YAML file to import from. Default will read from stdin.")
        )
        parser.add_argument(
            "-n",
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help=_("Make no changes to the database."),
        )
        parser.add_argument(
            "--force",
            action="store_true",
            dest="force",
            default=False,
            help=_("Make changes despite warnings."),
        )

    def handle(self, *args, **options):
        self._has_warnings = False  # pylint: disable=attribute-defined-outside-init
        self._has_errors = False  # pylint: disable=attribute-defined-outside-init

        try:
            import_data = load_data(options.get("file"))
        except ValueError as exc:
            self.stderr.write(self.style.ERROR(exc))
            return

        try:
            with transaction.atomic():
                for meeting_date, meeting_data in import_data.items():
                    self._process_meeting(meeting_date, meeting_data)
                if options["dry_run"] or self._has_errors or (self._has_warnings and not options["force"]):
                    raise DoRollback()
        except DoRollback:
            if self._has_errors:
                style = self.style.ERROR
            elif self._has_warnings and not options["force"]:
                style = self.style.WARNING
            else:
                style = self.style.SUCCESS
            self.stderr.write(style(_("Successfully processed import data, rolling back.")))

    def _process_meeting(self, meeting_date, meeting_data):
        meeting = Meeting(date=meeting_date)
        try:
            meeting.save()
        except IntegrityError:
            self.stderr.write(self.style.ERROR(_("Meeting data for %(date)s already exists") % {"date": meeting_date}))
            self._has_errors = True  # pylint: disable=attribute-defined-outside-init
            return None

        for role_name, role_data in meeting_data.items():
            self._process_role(meeting, role_name, role_data)

        self.stderr.write(self.style.SUCCESS(_("Processed meeting on %(date)s") % {"date": meeting_date}))
        return meeting

    def _process_role(self, meeting, role_name, role_data):
        try:
            role_type = RoleType.objects.get(name=role_name)
        except RoleType.DoesNotExist:
            self.stderr.write(self.style.ERROR(_("Role type %(name)s does not exist") % {"name": role_name}))
            self._has_errors = True  # pylint: disable=attribute-defined-outside-init
            return

        role = Role(meeting=meeting, role=role_type)
        role.save()

        if servers := role_data.get("serving"):
            self._process_servers(role, servers)

        if description := role_data.get("description"):
            role.description = description
            role.save()

        if location := role_data.get("location"):
            try:
                role.location = Location.objects.get(name=location)
                role.save()
            except Location.DoesNotExist:
                loc = Location(name=location)
                loc.save()
                role.location = loc
                role.save()
                self.stderr.write(self.style.WARNING(_("Added location %(name)s") % {"name": location}))
                self._has_warnings = True  # pylint: disable=attribute-defined-outside-init

    def _process_servers(self, role, servers):
        if isinstance(servers, str):
            servers = [servers]
        for server in servers:
            try:
                person = lookup_person(server)
                role.people.add(person)
            except Person.DoesNotExist:
                self.stderr.write(
                    self.style.WARNING(_("Server %(name)s will be treated as a guest") % {"name": server})
                )
                self._has_warnings = True  # pylint: disable=attribute-defined-outside-init
                role.guest = server
            role.save()
