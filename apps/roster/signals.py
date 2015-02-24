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


def default_roletypes(sender, **kwargs):
    r, created = RoleType.objects.get_or_create(name='Lesson')
    if created:
        r.verb = 'bring the lesson'
        r.order = 10
        r.save()

    r, created = RoleType.objects.get_or_create(name="Kid's Time")
    if created:
        r.verb = "lead Kid's Time"
        r.order = 20
        r.save()

    r, created = RoleType.objects.get_or_create(name='Focus Theme')
    if created:
        r.verb = 'lead the Focus Theme'
        r.order = 30
        r.save()

    r, created = RoleType.objects.get_or_create(name='Singing')
    if created:
        r.verb = 'lead the singing'
        r.order = 40
        r.save()

    r, created = RoleType.objects.get_or_create(name='Communion')
    if created:
        r.verb = 'lead Communion'
        r.order = 50
        r.save()

    r, created = RoleType.objects.get_or_create(name='Assisting Communion')
    if created:
        r.verb = 'assist with Communion'
        r.order = 60
        r.save()

    r, created = RoleType.objects.get_or_create(name='News Sharing')
    if created:
        r.verb = 'lead the announcements'
        r.order = 70
        r.save()

    r, created = RoleType.objects.get_or_create(name='Benediction')
    if created:
        r.verb = 'offer the benediction'
        r.order = 80
        r.save()

    r, created = RoleType.objects.get_or_create(name='Guest Teaching')
    if created:
        r.verb = 'be the guest teacher'
        r.order = 90
        r.save()

    r, created = RoleType.objects.get_or_create(name='Bible Study')
    if created:
        r.verb = 'lead the Bible study'
        r.order = 100
        r.save()

    r, created = RoleType.objects.get_or_create(name='Setup/Pack Up')
    if created:
        r.verb = 'assist with the set up and pack up'
        r.order = 110
        r.save()


post_migrate.connect(default_locations,
                     sender=apps.get_app_config('roster'))
post_migrate.connect(default_roletypes,
                     sender=apps.get_app_config('roster'))
