from django.apps import AppConfig


class DirectoryConfig(AppConfig):
    name = 'thepoint.apps.directory'

    def ready(self):
        import thepoint.apps.directory.signals  # noqa
