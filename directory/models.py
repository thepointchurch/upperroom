from django.conf import settings
from django.db import models

import calendar
from datetime import date

class CurrentManager(models.Manager):
    def get_queryset(self):
        return super(CurrentManager, self).get_queryset().filter(is_current=True)

class Family(models.Model):
    name = models.CharField(max_length=30)
    phone_home = models.CharField(max_length=10, null=True, blank=True, verbose_name='Home Phone')
    phone_mobile = models.CharField(max_length=10, null=True, blank=True, verbose_name='Mobile Phone')
    email = models.EmailField(null=True, blank=True)
    street = models.CharField(max_length=32, null=True, blank=True)
    suburb = models.CharField(max_length=32, null=True, blank=True)
    postcode = models.CharField(max_length=6, null=True, blank=True)
    is_current = models.BooleanField(default=True, verbose_name='Current')

    husband = models.ForeignKey('Person', null=True, blank=True, related_name='+')
    wife = models.ForeignKey('Person', null=True, blank=True, related_name='+')
    anniversary = models.DateField(null=True, blank=True)

    current_objects = CurrentManager()
    objects = models.Manager()

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'families'

    def __str__(self):
        return self.name

    def spouse_ids(self):
        ids = []
        if self.husband: ids.append(self.husband.id)
        if self.wife: ids.append(self.wife.id)
        return ids

    @property
    def spouses(self):
        return self.members.filter(id__in=self.spouse_ids())

    @property
    def siblings(self):
        return self.members.exclude(id__in=self.spouse_ids())

    @property
    def anniversarydate(self):
        return self.anniversary.replace(year=2000)

    @property
    def first_letter(self):
        return self.name[0].lower()

    @property
    def marriage(self):
        if self.husband and self.wife:
            return '%s and %s %s' % (self.husband.name, self.wife.name, self.name)

    def save(self, *args, **kwargs):
        super(Family, self).save(*args, **kwargs)
        for member in self.members.all():
            if member.user:
                member.user.last_name = self.name
                if self.email and not member.email:
                    member.user.email = self.email
            if not self.is_current:
                member.is_current = False
            member.save()
    
class Person(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True)
    family = models.ForeignKey(Family, related_name='members')

    order = models.SmallIntegerField(null=True, blank=True)

    name = models.CharField(max_length=30)
    suffix = models.CharField(max_length=3, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_mobile = models.CharField(max_length=10, null=True, blank=True, verbose_name='Mobile Phone')
    phone_work = models.CharField(max_length=10, null=True, blank=True, verbose_name='Work Phone')
    is_member = models.BooleanField(default=True, verbose_name='Member')
    is_current = models.BooleanField(default=True, verbose_name='Current')

    current_objects = CurrentManager()
    objects = models.Manager()

    class Meta:
        ordering = ['order', 'id', 'name'] # I wish there was a better way???
        verbose_name_plural = 'people'

    def __str__(self):
        return self.fullname

    @property
    def fullname(self):
        if self.suffix:
            return '%s %s (%s)' % (self.name, self.family.name, self.suffix)
        return '%s %s' % (self.name, self.family.name)

    @property
    def name_with_suffix(self):
        if self.suffix:
            return '%s (%s)' % (self.name, self.suffix)
        return self.name

    @property
    def birthdate(self):
        return self.birthday.replace(year=2000)

    @property
    def has_roster(self):
        if self.roles.count() > 0: return True
        return False

    def find_email(self):
        if self.email: return self.email
        if self.family.email: return self.family.email

    def save(self, *args, **kwargs):
        super(Person, self).save(*args, **kwargs)
        if self.user:
            self.user.first_name = self.name
            self.user.last_name = self.family.name
            self.user.email = self.email or self.family.email
            self.user.save()
