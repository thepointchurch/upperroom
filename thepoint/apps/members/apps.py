from django.apps import AppConfig


class MembersConfig(AppConfig):
    name = 'thepoint.apps.members'

    def ready(self):
        import thepoint.apps.members.signals  # noqa
