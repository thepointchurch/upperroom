from django.apps import AppConfig


class ExtendedSitesConfig(AppConfig):
    name = "upperroom.extendedsites"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import upperroom.extendedsites.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
