from datetime import time

from django.apps import apps
from django.db.models.signals import post_migrate
from django.utils.translation import ugettext_lazy as _

from roster.models import Location, RoleType


def default_locations(sender, **kwargs):
    Location.objects.get_or_create(name=_('Gold Coast'))
    Location.objects.get_or_create(name=_('Maryborough'))
    Location.objects.get_or_create(name=_('Morayfield'))
    Location.objects.get_or_create(name=_('Sunshine Coast'))
    Location.objects.get_or_create(name=_('Warwick'))
    Location.objects.get_or_create(name=_('Wynnum'))


def _ensure_role_type(name, verb, order, start_time, end_time):
    r, created = RoleType.objects.get_or_create(name=name)
    if created:
        r.verb = verb
        r.order = order
        r.start_time = start_time
        r.end_time = end_time
        r.save()


def default_roletypes(sender, **kwargs):
    _ensure_role_type(name=_('Lesson'),
                      verb=_('bring the lesson'),
                      order=10,
                      start_time=time(9, 30),
                      end_time=time(10, 0))

    _ensure_role_type(name=_("Kid's Time"),
                      verb=_("lead Kid's Time"),
                      order=20,
                      start_time=time(9, 30),
                      end_time=time(9, 45))

    _ensure_role_type(name=_('Focus Theme'),
                      verb=_('lead the Focus Theme'),
                      order=30,
                      start_time=time(9, 45),
                      end_time=time(10, 0))

    _ensure_role_type(name=_('Singing'),
                      verb=_('lead the singing'),
                      order=40,
                      start_time=time(11, 15),
                      end_time=time(11, 30))

    _ensure_role_type(name=_('Communion'),
                      verb=_('lead Communion'),
                      order=50,
                      start_time=time(11, 30),
                      end_time=time(11, 45))

    _ensure_role_type(name=_('Assisting Communion'),
                      verb=_('assist with Communion'),
                      order=60,
                      start_time=time(11, 30),
                      end_time=time(11, 45))

    _ensure_role_type(name=_('News Sharing'),
                      verb=_('lead the announcements'),
                      order=70,
                      start_time=time(11, 45),
                      end_time=time(12, 0))

    _ensure_role_type(name=_('Benediction'),
                      verb=_('offer the benediction'),
                      order=80,
                      start_time=time(11, 45),
                      end_time=time(12, 0))

    _ensure_role_type(name=_('Guest Teaching'),
                      verb=_('be the guest teacher'),
                      order=90,
                      start_time=time(9, 30),
                      end_time=time(11, 30))

    _ensure_role_type(name=_('Bible Study'),
                      verb=_('lead the Bible study'),
                      order=100,
                      start_time=time(19, 30),
                      end_time=time(20, 30))

    _ensure_role_type(name=_('Setup/Pack Up'),
                      verb=_('assist with the set up and pack up'),
                      order=110,
                      start_time=time(11, 45),
                      end_time=time(12, 0))


post_migrate.connect(default_locations,
                     sender=apps.get_app_config('roster'))
post_migrate.connect(default_roletypes,
                     sender=apps.get_app_config('roster'))
