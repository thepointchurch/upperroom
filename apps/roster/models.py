from datetime import date, datetime, timedelta

from django.db import models

from directory.models import Person


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
    date = models.DateField(primary_key=True, default=next_empty_meeting_date)

    current_objects = CurrentManager()
    objects = models.Manager()

    class Meta:
        ordering = ['date']
        get_latest_by = 'date'
        verbose_name_plural = 'meetings'

    def __str__(self):
        return str(self.date)


class Location(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'locations'

    def __str__(self):
        return self.name


class RoleType(models.Model):
    name = models.CharField(max_length=30)
    verb = models.CharField(max_length=50)
    order = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ['order']
        verbose_name_plural = 'roletypes'

    def __str__(self):
        return self.name


class CurrentRoleManager(models.Manager):
    def get_queryset(self):
        return super(CurrentRoleManager,
                     self).get_queryset()\
            .filter(meeting__date__gte=date.today())


class Role(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    revision = models.PositiveIntegerField(default=0)

    meeting = models.ForeignKey(Meeting, related_name='roles')

    people = models.ManyToManyField(Person, blank=True,
                                    limit_choices_to={'is_current': True},
                                    related_name='roles')
    guest = models.CharField(max_length=30, null=True, blank=True)
    role = models.ForeignKey(RoleType, related_name='roles')
    description = models.CharField(max_length=64, null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True,
                                 related_name='roles')

    current_objects = CurrentRoleManager()
    objects = models.Manager()

    class Meta:
        ordering = ['role']
        verbose_name_plural = 'roles'

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
                        self.meeting.date.day, 9, 30) - timedelta(hours=10)

    @property
    def endtime(self):
        return datetime(self.meeting.date.year,
                        self.meeting.date.month,
                        self.meeting.date.day, 12, 0) - timedelta(hours=10)

    def save(self, *args, **kwargs):
        self.revision += 1
        super(Role, self).save(*args, **kwargs)
