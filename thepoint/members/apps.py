from django.apps import AppConfig


class MembersConfig(AppConfig):
    name = "thepoint.members"

    def ready(self):
        import thepoint.members.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
