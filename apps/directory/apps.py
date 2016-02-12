from django.apps import AppConfig


class DirectoryAppConfig(AppConfig):
    name = 'directory'

    def ready(self):
        import directory.signals  # noqa
