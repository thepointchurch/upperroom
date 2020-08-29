from django.apps import AppConfig


class WeblogConfig(AppConfig):
    name = "thepoint.apps.weblog"

    def ready(self):
        import thepoint.apps.weblog.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
