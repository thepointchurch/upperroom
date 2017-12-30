from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    name = 'thepoint.apps.resources'

    def ready(self):
        import thepoint.apps.resources.signals  # noqa
