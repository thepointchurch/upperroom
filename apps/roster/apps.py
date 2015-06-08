from django.apps import AppConfig


class RosterAppConfig(AppConfig):
    name = 'roster'

    def ready(self):
        import roster.signals  # noqa
