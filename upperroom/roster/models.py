from datetime import date, datetime, time, timedelta

from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

DAYS_OF_THE_WEEK = (
    (1, _("Sunday")),
    (2, _("Monday")),
    (3, _("Tuesday")),
    (4, _("Wednesday")),
    (5, _("Thursday")),
    (6, _("Friday")),
    (7, _("Saturday")),
)


def next_empty_meeting_date(weekday=None):
    if weekday is None:
        weekday = 1
    try:
        max_date = Meeting.objects.filter(date__week_day=weekday).latest().date
        return max_date + timedelta(7)
    except Exception:  # pylint: disable=broad-except
        max_date = date.today()
        return max_date + timedelta((6 - max_date.weekday()) % 6)


class CurrentManager(models.Manager):  # pylint: disable=too-few-public-methods
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(date__gte=date.today())
            .prefetch_related("roles__people__family", "roles__role", "roles__location")
        )


class Meeting(models.Model):
    date = models.DateField(unique=True, default=next_empty_meeting_date, verbose_name=_("date"))

    current_objects = CurrentManager()
    objects = models.Manager()

    class Meta:
        ordering = ["date"]
        get_latest_by = "date"
        verbose_name = _("meeting")
        verbose_name_plural = _("meetings")

    def __str__(self):
        return str(self.date)

    def save(self, *args, **kwargs):  # pylint: disable=signature-differs
        # Update roles when the meeting is updated
        for role in self.roles.all():
            role.save()
        super().save(*args, **kwargs)

    def merged_roles(self):
        def my_model_to_dict(i):
            j = model_to_dict(i)
            j["role"] = i.role
            j["name"] = i.role.name
            j["order"] = i.role.order
            j["location"] = i.location.name if i.location else ""  # '' required for regroup to work in the template
            j["print"] = i.role.include_in_print
            return j

        parents = {}
        for role in self.roles.filter(role__parent__isnull=False):
            if (role.role.parent, role.location, role.guest, role.description) not in parents:
                parents[(role.role.parent, role.location, role.guest, role.description)] = []
            parents[(role.role.parent, role.location, role.guest, role.description)].append(role)
        parent_roles = []
        for (role, __, __, __), people in parents.items():
            parent_role = my_model_to_dict(Role(meeting=self, role=role))
            for person in people:
                parent_role["people"].extend(list(person.people.all()))
            parent_roles.append(parent_role)
        return sorted(
            [my_model_to_dict(r) for r in self.roles.filter(role__parent__isnull=True)] + parent_roles,
            key=lambda x: x["order"],
        )


class Location(models.Model):
    name = models.CharField(max_length=30, verbose_name=_("name"))

    class Meta:
        ordering = ["name"]
        verbose_name = _("location")
        verbose_name_plural = _("locations")

    def __str__(self):
        return self.name


class RoleType(models.Model):
    name = models.CharField(max_length=30, verbose_name=_("name"))
    verb = models.CharField(max_length=50, verbose_name=_("verb"))
    order = models.PositiveSmallIntegerField(default=100, verbose_name=_("order"))
    start_time = models.TimeField(default=time(9, 30), verbose_name=_("start time"))
    end_time = models.TimeField(default=time(10, 0), verbose_name=_("end time"))
    servers = models.ManyToManyField(
        "directory.Person",
        blank=True,
        limit_choices_to={"is_current": True},
        related_name="role_types",
        verbose_name=_("servers"),
    )
    include_in_print = models.BooleanField(default=True, verbose_name=_("include in printout"))
    order_by_age = models.BooleanField(default=True, verbose_name=_("order by age"))
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children", verbose_name=_("parent"),
    )

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["order"]),
        ]
        verbose_name = _("role type")
        verbose_name_plural = _("role types")

    def __str__(self):
        return self.name


class CurrentRoleManager(models.Manager):  # pylint: disable=too-few-public-methods
    def get_queryset(self):
        return super().get_queryset().filter(meeting__date__gte=date.today())


class Role(models.Model):
    timestamp = models.DateTimeField(auto_now=True, verbose_name=_("timestamp"))
    revision = models.PositiveIntegerField(default=0, verbose_name=_("revision"))

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="roles", verbose_name=_("meeting"))

    people = models.ManyToManyField(
        "directory.Person",
        blank=True,
        limit_choices_to={"is_current": True},
        related_name="roles",
        verbose_name=_("people"),
    )
    guest = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("guest"))
    role = models.ForeignKey(
        RoleType,
        on_delete=models.PROTECT,
        limit_choices_to=models.Q(children__isnull=True),
        related_name="roles",
        verbose_name=_("role"),
    )
    description = models.CharField(max_length=64, null=True, blank=True, verbose_name=_("description"))
    location = models.ForeignKey(
        Location, null=True, blank=True, on_delete=models.PROTECT, related_name="roles", verbose_name=_("location"),
    )

    objects = models.Manager()
    current_objects = CurrentRoleManager()

    class Meta:
        ordering = ["role"]
        verbose_name = _("role")
        verbose_name_plural = _("roles")

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.role.name

    @property
    def is_guest(self):
        if self.guest:
            return True
        return False

    @property
    def date(self):
        return self.meeting.date

    @property
    def starttime(self):
        return datetime(
            self.meeting.date.year,
            self.meeting.date.month,
            self.meeting.date.day,
            self.role.start_time.hour,
            self.role.start_time.minute,
        ) - timedelta(hours=10)

    @property
    def endtime(self):
        return datetime(
            self.meeting.date.year,
            self.meeting.date.month,
            self.meeting.date.day,
            self.role.end_time.hour,
            self.role.end_time.minute,
        ) - timedelta(hours=10)

    def save(self, *args, **kwargs):  # pylint: disable=signature-differs
        self.revision += 1
        super().save(*args, **kwargs)


class MeetingTemplate(models.Model):
    name = models.CharField(max_length=30, verbose_name=_("name"))
    is_default = models.BooleanField(default=False, verbose_name=_("is default"))
    week_day = models.SmallIntegerField(null=True, blank=True, choices=DAYS_OF_THE_WEEK, verbose_name=_("week day"))
    roles = models.ManyToManyField(
        RoleType, through="RoleTypeTemplateMapping", blank=True, related_name="templates", verbose_name=_("roles"),
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("meeting template")
        verbose_name_plural = _("meeting templates")

    def __str__(self):
        return self.name


class RoleTypeTemplateMapping(models.Model):
    template = models.ForeignKey(MeetingTemplate, on_delete=models.CASCADE)
    role_type = models.ForeignKey(RoleType, on_delete=models.CASCADE)
    order = models.SmallIntegerField(null=True, blank=True, verbose_name=_("order"))

    def __str__(self):
        return self.role_type.name
