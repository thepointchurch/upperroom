from django.apps import AppConfig


class WeblogConfig(AppConfig):
    name = "thepoint.weblog"

    def ready(self):
        import thepoint.weblog.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
