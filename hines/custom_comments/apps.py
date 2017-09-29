from django.apps import AppConfig


class CustomCommentsConfig(AppConfig):
    name = 'hines.custom_comments'
    verbose_name = 'Comments'

    def ready(self):
        import hines.custom_comments.signals

