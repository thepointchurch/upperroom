from django.apps import AppConfig


class LibraryConfig(AppConfig):
    name = "upperroom.library"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import upperroom.library.portals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
