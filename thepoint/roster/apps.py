from django.apps import AppConfig


class RosterConfig(AppConfig):
    name = "thepoint.roster"

    def ready(self):
        import thepoint.roster.portals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
