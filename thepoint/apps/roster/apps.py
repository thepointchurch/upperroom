from django.apps import AppConfig


class RosterConfig(AppConfig):
    name = 'thepoint.apps.roster'

    def ready(self):
        import thepoint.apps.roster.signals  # noqa
