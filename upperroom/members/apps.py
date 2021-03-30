from django.apps import AppConfig


class MembersConfig(AppConfig):
    name = "upperroom.members"

    def ready(self):
        import upperroom.members.signals  # NOQA: F401 pylint: disable=import-outside-toplevel,unused-import
