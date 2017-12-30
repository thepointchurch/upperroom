from datetime import date, datetime, time, timedelta

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..directory.models import Person


def next_empty_meeting_date():
    try:
        max = Meeting.objects.latest().date
    except:
        max = None
    if not max:
        max = date.today()
    if max.weekday() == 6:
        return max + timedelta(7)
    return max + timedelta(6 - max.weekday())


class CurrentManager(models.Manager):
    def get_queryset(self):
        return super(CurrentManager,
                     self).get_queryset().filter(date__gte=date.today())


class Meeting(models.Model):
    date = models.DateField(
        unique=True,
        default=next_empty_meeting_date,
        verbose_name=_('date'),
    )

    current_objects = CurrentManager()
    objects = models.Manager()

    class Meta:
        ordering = ['date']
        get_latest_by = 'date'
        verbose_name = _('meeting')
        verbose_name_plural = _('meetings')

    def __str__(self):
        return str(self.date)


class Location(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name=_('name'),
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('location')
        verbose_name_plural = _('locations')

    def __str__(self):
        return self.name


class RoleType(models.Model):
    name = models.CharField(
        max_length=30,
        verbose_name=_('name'),
    )
    verb = models.CharField(
        max_length=50,
        verbose_name=_('verb'),
    )
    order = models.PositiveSmallIntegerField(
        default=100,
        verbose_name=_('order'),
    )
    start_time = models.TimeField(
        default=time(9, 30),
        verbose_name=_('start time'),
    )
    end_time = models.TimeField(
        default=time(10, 0),
        verbose_name=_('end time'),
    )

    class Meta:
        ordering = ['order']
        verbose_name = _('role type')
        verbose_name_plural = _('role types')

    def __str__(self):
        return self.name


class CurrentRoleManager(models.Manager):
    def get_queryset(self):
        return (super(CurrentRoleManager,
                      self).get_queryset()
                           .filter(meeting__date__gte=date.today()))


class Role(models.Model):
    timestamp = models.DateTimeField(
        auto_now=True,
        verbose_name=_('timestamp'),
    )
    revision = models.PositiveIntegerField(
        default=0,
        verbose_name=_('revision'),
    )

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name=_('meeting'),
    )

    people = models.ManyToManyField(
        Person,
        blank=True,
        limit_choices_to={'is_current': True},
        related_name='roles',
        verbose_name=_('people'),
    )
    guest = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name=_('guest'),
    )
    role = models.ForeignKey(
        RoleType,
        on_delete=models.PROTECT,
        related_name='roles',
        verbose_name=_('role'),
    )
    description = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=_('description'),
    )
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='roles',
        verbose_name=_('location'),
    )

    current_objects = CurrentRoleManager()
    objects = models.Manager()

    class Meta:
        ordering = ['role']
        verbose_name = _('role')
        verbose_name_plural = _('roles')

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
        return datetime(self.meeting.date.year,
                        self.meeting.date.month,
                        self.meeting.date.day,
                        self.role.start_time.hour,
                        self.role.start_time.minute) - timedelta(hours=10)

    @property
    def endtime(self):
        return datetime(self.meeting.date.year,
                        self.meeting.date.month,
                        self.meeting.date.day,
                        self.role.end_time.hour,
                        self.role.end_time.minute) - timedelta(hours=10)

    def save(self, *args, **kwargs):
        self.revision += 1
        super(Role, self).save(*args, **kwargs)
