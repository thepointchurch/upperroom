import base64
import re
from datetime import date

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _


class CurrentManager(models.Manager):  # pylint: disable=too-few-public-methods
    def get_queryset(self):
        return super().get_queryset().filter(is_current=True)


def get_family_photo_filename(instance, filename):  # pylint: disable=unused-argument
    return "directory/family/%d/photo.jpg" % instance.id


def get_family_thumbnail_filename(instance, filename):  # pylint: disable=unused-argument
    return "directory/family/%d/thumbnail.jpg" % instance.id


class Family(models.Model):
    name = models.CharField(max_length=30, verbose_name=_("name"))
    phone_home = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("home phone"))
    phone_mobile = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("mobile phone"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("email"))
    street = models.CharField(max_length=128, null=True, blank=True, verbose_name=_("street"))
    suburb = models.CharField(max_length=32, null=True, blank=True, verbose_name=_("suburb"))
    postcode = models.CharField(max_length=6, null=True, blank=True, verbose_name=_("postcode"))
    is_current = models.BooleanField(default=True, verbose_name=_("current"))

    husband = models.ForeignKey(
        "Person", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("husband"),
    )
    wife = models.ForeignKey(
        "Person", null=True, blank=True, on_delete=models.SET_NULL, related_name="+", verbose_name=_("wife"),
    )
    anniversary = models.DateField(null=True, blank=True, verbose_name=_("anniversary"))

    photo = models.ImageField(null=True, blank=True, upload_to=get_family_photo_filename)
    photo_thumbnail = models.ImageField(
        null=True, blank=True, editable=False, upload_to=get_family_thumbnail_filename,
    )

    objects = models.Manager()
    current_objects = CurrentManager()

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_current"]),
        ]
        verbose_name = _("family")
        verbose_name_plural = _("families")
        permissions = [
            ("can_view", "Can view the directory"),
        ]

    def __str__(self):
        members = []
        people = self.members.all()
        if self.is_current:
            people = people.filter(is_current=True)
        for member in people:
            members.append(member.name)
        return "%s (%s)" % (self.name, ", ".join(members))

    def spouse_ids(self):
        ids = []
        if self.husband and self.husband.is_current:
            ids.append(self.husband.id)
        if self.wife and self.wife.is_current:
            ids.append(self.wife.id)
        return ids

    @cached_property
    def current_members(self):
        return self.members.filter(is_current=True)

    @cached_property
    def spouses(self):
        return self.current_members.filter(id__in=self.spouse_ids())

    @cached_property
    def siblings(self):
        return self.current_members.exclude(id__in=self.spouse_ids())

    @cached_property
    def anniversarydate(self):
        return self.anniversary.replace(year=2000)

    @cached_property
    def anniversary_age(self):
        if self.anniversary:
            today = date.today()
            this_year = self.anniversary.replace(year=today.year)
            age = today.year - self.anniversary.year
            if this_year > today:
                age -= 1
            return age
        return None

    @property
    def phone_home_intl(self):
        return re.sub(r"^0", "+61", self.phone_home.replace(" ", ""))

    @property
    def phone_mobile_intl(self):
        return re.sub(r"^0", "+61", self.phone_mobile.replace(" ", ""))

    @property
    def first_letter(self):
        return self.name[0].lower()

    @cached_property
    def photo_base64(self):
        return base64.b64encode(self.photo.file.file.read()).decode("ascii")

    def get_absolute_url(self):
        return reverse("directory:detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):  # pylint: disable=signature-differs
        super().save(*args, **kwargs)
        for member in self.members.all():
            if member.user:
                member.user.last_name = self.name
                if self.email and not member.email:
                    member.user.email = self.email
            member.is_current = self.is_current
            member.save()


class Person(models.Model):
    GENDER_MALE = "M"
    GENDER_FEMALE = "F"
    GENDER_CHOICES = (
        (GENDER_MALE, _("Male")),
        (GENDER_FEMALE, _("Female")),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, verbose_name=_("user"),
    )
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="members", verbose_name=_("family"))

    order = models.SmallIntegerField(null=True, blank=True, verbose_name=_("order"))

    name = models.CharField(max_length=30, verbose_name=_("name"))
    suffix = models.CharField(max_length=3, null=True, blank=True, verbose_name=_("suffix"))
    surname_override = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("surname"))
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True, verbose_name=_("gender"))
    birthday = models.DateField(null=True, blank=True, verbose_name=_("birthday"))
    email = models.EmailField(null=True, blank=True, verbose_name=_("email"))
    phone_mobile = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("mobile phone"))
    phone_work = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("work phone"))
    is_member = models.BooleanField(default=True, verbose_name=_("member"))
    is_current = models.BooleanField(default=True, verbose_name=_("current"))

    objects = models.Manager()
    current_objects = CurrentManager()

    class Meta:
        ordering = ["order", "id", "name"]  # I wish there was a better way
        indexes = [
            models.Index(fields=["order", "id", "name"]),
            models.Index(fields=["is_current"]),
        ]
        verbose_name = _("person")
        verbose_name_plural = _("people")

    def __str__(self):
        return self.fullname

    @property
    def fullname(self):
        if self.suffix:
            return "%s %s (%s)" % (self.name, self.surname, self.suffix)
        return "%s %s" % (self.name, self.surname)

    @property
    def name_with_suffix(self):
        if self.suffix:
            return "%s (%s)" % (self.name, self.suffix)
        return self.name

    @property
    def surname(self):
        if self.surname_override:
            return self.surname_override
        return self.family.name

    @property
    def birthdate(self):
        return self.birthday.replace(year=2000)

    @property
    def phone_mobile_intl(self):
        return re.sub(r"^0", "+61", self.phone_mobile.replace(" ", ""))

    @property
    def phone_work_intl(self):
        return re.sub(r"^0", "+61", self.phone_work.replace(" ", ""))

    @cached_property
    def has_roster(self):
        if self.roles.count() > 0:
            return True
        return False

    def find_email(self):
        if self.email:
            return self.email
        if self.family.email:
            return self.family.email
        return None

    def save(self, *args, **kwargs):  # pylint: disable=signature-differs
        super().save(*args, **kwargs)
        if self.user:
            self.user.first_name = self.name
            self.user.last_name = self.surname
            self.user.email = self.email or self.family.email
            self.user.save()
