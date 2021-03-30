from django.apps import AppConfig


class RosterConfig(AppConfig):
    name = "upperroom.roster"

    def ready(self):
        import upperroom.roster.portals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
