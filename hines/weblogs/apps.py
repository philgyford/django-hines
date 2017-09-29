from django.apps import AppConfig


class WeblogsConfig(AppConfig):
    name = 'hines.weblogs'
    verbose_name = 'Weblogs'

    def ready(self):
        import hines.weblogs.signals

