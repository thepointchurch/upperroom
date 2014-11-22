from django.db import models

from datetime import date, timedelta

from directory.models import Person

def next_meeting():
    max = Meeting.objects.latest().date
    if not max: max = date.today()
    if max.weekday() == 6: return max + timedelta(7)
    return max + timedelta(6 - max.weekday())

class Meeting(models.Model):
    date = models.DateField(unique=True, default=next_meeting)

    class Meta:
        ordering = ['date']
        get_latest_by = 'date'
        verbose_name_plural = 'meetings'

    def __str__(self):
        return str(self.date)

    def clean(self):
        if self.date.weekday() != 6:
            self.date = self.date + timedelta(6 - self.date.weekday())

class Role(models.Model):
    ANNOUNCE =   'ANN'
    LSUP =       'LSU'
    LSUPASSIST = 'LSA'
    SERMON =     'SER'
    SONGS =      'SON'
    PRAISE =     'PRA'
    KIDS =       'KID'
    GUESTTEACH = 'GUE'
    BENEDICT =   'BEN'
    ROLES = (
        (ANNOUNCE,   'News Sharing'),
        (LSUP,       'Communion'),
        (LSUPASSIST, 'Assisting Communion'),
        (SERMON,     'Lesson'),
        (SONGS,      'Singing'),
        (PRAISE,     'Focus Theme'),
        (KIDS,       "Kid's Time"),
        (GUESTTEACH, 'Guest Teaching'),
        (BENEDICT,   'Benediction'),
    )

    LOCATIONS = (
        ('GC', 'Gold Coast'),
        ('MA', 'Maryborough'),
        ('MO', 'Morayfield'),
        ('SC', 'Sunshine Coast'),
        ('WA', 'Warwick'),
        ('WY', 'Wynnum'),
    )

    timestamp = models.DateTimeField(auto_now=True)
    revision = models.PositiveIntegerField(default=0)

    meeting = models.ForeignKey(Meeting, related_name='roles')

    person = models.ForeignKey(Person, null=True, blank=True, limit_choices_to={'is_current': True, 'is_member': True, 'gender': 'M'})
    guest = models.CharField(max_length=30, null=True, blank=True)
    models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), null=True, blank=True)
    role = models.CharField(max_length=3, choices=ROLES)
    description = models.CharField(max_length=64, null=True, blank=True)
    location = models.CharField(max_length=2, choices=LOCATIONS, null=True, blank=True)

    class Meta:
        ordering = ['role', 'person__name']
        verbose_name_plural = 'roles'

    def __str__(self):
        return '%s %s' % (self.get_role_display(), self.name)

    @property
    def name(self):
        if self.person: return self.person.fullname
        if self.guest: return self.guest

    @property
    def date(self):
        return meeting.date

    def save(self, *args, **kwargs):
        self.revision += 1
        super(Role, self).save(*args, **kwargs)
