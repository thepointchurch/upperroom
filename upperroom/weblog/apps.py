from django.apps import AppConfig


class WeblogConfig(AppConfig):
    name = "upperroom.weblog"

    def ready(self):
        import upperroom.weblog.portals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
        import upperroom.weblog.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
