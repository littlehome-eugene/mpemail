from django.apps import AppConfig


class EmailConfig(AppConfig):
    name = 'mpemail'

    def ready(self):

        import mpemail.signals.email