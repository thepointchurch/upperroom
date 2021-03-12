from django.apps import AppConfig


class NewsletterConfig(AppConfig):
    name = "thepoint.newsletter"

    def ready(self):
        import thepoint.newsletter.portals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
