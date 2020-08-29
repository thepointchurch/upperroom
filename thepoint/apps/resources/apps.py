from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    name = "thepoint.apps.resources"

    def ready(self):
        import thepoint.apps.resources.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
