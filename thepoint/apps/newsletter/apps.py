from django.apps import AppConfig


class NewsletterConfig(AppConfig):
    name = 'thepoint.apps.newsletter'

    def ready(self):
        import thepoint.apps.newsletter.signals  # noqa
