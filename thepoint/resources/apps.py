from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    name = "thepoint.resources"

    def ready(self):
        import thepoint.resources.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
