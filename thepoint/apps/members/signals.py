from django.apps import apps
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


def add_permissions(sender, **kwargs):
    g, created = Group.objects.get_or_create(name=_('Guests'))

    content_type = ContentType.objects.get_for_model(User)
    permission, created = Permission.objects.get_or_create(
        codename='can_view', name=_('Can add user'), content_type=content_type)

    g.permissions.add(permission)
    g.save()


post_migrate.connect(add_permissions, sender=apps.get_app_config('members'))
