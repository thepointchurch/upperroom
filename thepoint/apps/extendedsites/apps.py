from django.apps import AppConfig


class ExtendedSitesConfig(AppConfig):
    name = 'thepoint.apps.extendedsites'

    def ready(self):
        import thepoint.apps.extendedsites.signals  # noqa
