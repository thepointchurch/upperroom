from django.apps import AppConfig

class MembersAppConfig(AppConfig):
    name = 'members'

    def ready(self):
        import members.signals
