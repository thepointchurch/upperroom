from django.apps import AppConfig


class NewsletterConfig(AppConfig):
    name = "upperroom.newsletter"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import upperroom.newsletter.portals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
