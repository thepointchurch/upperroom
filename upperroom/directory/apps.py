from django.apps import AppConfig


class DirectoryConfig(AppConfig):
    name = "upperroom.directory"

    def ready(self):
        import upperroom.directory.portals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
        import upperroom.directory.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
