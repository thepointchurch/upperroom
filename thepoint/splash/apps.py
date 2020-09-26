from django.apps import AppConfig


class SplashConfig(AppConfig):
    name = "thepoint.splash"

    def ready(self):
        import thepoint.splash.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
