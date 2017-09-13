from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    name = "account"
    verbose_name = "account"

    def ready(self):
        import account.signals
