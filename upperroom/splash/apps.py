from django.apps import AppConfig


class SplashConfig(AppConfig):
    name = "upperroom.splash"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import upperroom.splash.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
