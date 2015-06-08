from django.apps import AppConfig


class NewsletterAppConfig(AppConfig):
    name = 'newsletter'

    def ready(self):
        import newsletter.signals  # noqa
