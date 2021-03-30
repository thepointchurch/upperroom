from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    name = "upperroom.resources"

    def ready(self):
        import upperroom.resources.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
