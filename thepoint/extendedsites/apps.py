from django.apps import AppConfig


class ExtendedSitesConfig(AppConfig):
    name = "thepoint.extendedsites"

    def ready(self):
        import thepoint.extendedsites.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
