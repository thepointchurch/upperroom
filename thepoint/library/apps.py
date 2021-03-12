from django.apps import AppConfig


class LibraryConfig(AppConfig):
    name = "thepoint.library"

    def ready(self):
        import thepoint.library.portals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
