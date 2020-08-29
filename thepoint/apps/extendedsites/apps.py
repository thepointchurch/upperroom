from django.apps import AppConfig


class ExtendedSitesConfig(AppConfig):
    name = "thepoint.apps.extendedsites"

    def ready(self):
        import thepoint.apps.extendedsites.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
