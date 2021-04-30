from django.apps import AppConfig


class DirectoryConfig(AppConfig):
    name = "upperroom.directory"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import upperroom.directory.portals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
        import upperroom.directory.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
