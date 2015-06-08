from django.apps import AppConfig


class ResourcesAppConfig(AppConfig):
    name = 'resources'

    def ready(self):
        import resources.signals  # noqa
