from django.apps import AppConfig


class DirectoryConfig(AppConfig):
    name = "thepoint.directory"

    def ready(self):
        import thepoint.directory.portals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
        import thepoint.directory.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
