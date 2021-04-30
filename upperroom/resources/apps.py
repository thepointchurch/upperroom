from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    name = "upperroom.resources"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import upperroom.resources.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
