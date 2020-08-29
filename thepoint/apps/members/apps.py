from django.apps import AppConfig


class MembersConfig(AppConfig):
    name = "thepoint.apps.members"

    def ready(self):
        import thepoint.apps.members.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
