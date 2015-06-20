from datetime import time

from django.apps import apps
from django.db.models.signals import post_migrate

from roster.models import Location, RoleType


def default_locations(sender, **kwargs):
    Location.objects.get_or_create(name='Gold Coast')
    Location.objects.get_or_create(name='Maryborough')
    Location.objects.get_or_create(name='Morayfield')
    Location.objects.get_or_create(name='Sunshine Coast')
    Location.objects.get_or_create(name='Warwick')
    Location.objects.get_or_create(name='Wynnum')


def _ensure_role_type(name, verb, order, start_time, end_time):
    r, created = RoleType.objects.get_or_create(name=name)
    if created:
        r.verb = verb
        r.order = order
        r.start_time = start_time
        r.end_time = end_time
        r.save()


def default_roletypes(sender, **kwargs):
    _ensure_role_type(name='Lesson',
                      verb='bring the lesson',
                      order=10,
                      start_time=time(9, 30),
                      end_time=time(10, 0))

    _ensure_role_type(name="Kid's Time",
                      verb="lead Kid's Time",
                      order=20,
                      start_time=time(9, 30),
                      end_time=time(9, 45))

    _ensure_role_type(name='Focus Theme',
                      verb='lead the Focus Theme',
                      order=30,
                      start_time=time(9, 45),
                      end_time=time(10, 0))

    _ensure_role_type(name='Singing',
                      verb='lead the singing',
                      order=40,
                      start_time=time(11, 15),
                      end_time=time(11, 30))

    _ensure_role_type(name='Communion',
                      verb='lead Communion',
                      order=50,
                      start_time=time(11, 30),
                      end_time=time(11, 45))

    _ensure_role_type(name='Assisting Communion',
                      verb='assist with Communion',
                      order=60,
                      start_time=time(11, 30),
                      end_time=time(11, 45))

    _ensure_role_type(name='News Sharing',
                      verb='lead the announcements',
                      order=70,
                      start_time=time(11, 45),
                      end_time=time(12, 0))

    _ensure_role_type(name='Benediction',
                      verb='offer the benediction',
                      order=80,
                      start_time=time(11, 45),
                      end_time=time(12, 0))

    _ensure_role_type(name='Guest Teaching',
                      verb='be the guest teacher',
                      order=90,
                      start_time=time(9, 30),
                      end_time=time(11, 30))

    _ensure_role_type(name='Bible Study',
                      verb='lead the Bible study',
                      order=100,
                      start_time=time(19, 30),
                      end_time=time(20, 30))

    _ensure_role_type(name='Setup/Pack Up',
                      verb='assist with the set up and pack up',
                      order=110,
                      start_time=time(11, 45),
                      end_time=time(12, 0))


post_migrate.connect(default_locations,
                     sender=apps.get_app_config('roster'))
post_migrate.connect(default_roletypes,
                     sender=apps.get_app_config('roster'))
