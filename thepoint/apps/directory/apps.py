from django.apps import AppConfig


class DirectoryConfig(AppConfig):
    name = "thepoint.apps.directory"

    def ready(self):
        import thepoint.apps.directory.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
