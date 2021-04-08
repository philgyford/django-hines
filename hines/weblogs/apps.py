from django.apps import AppConfig


class WeblogsConfig(AppConfig):
    name = "hines.weblogs"
    verbose_name = "Weblogs"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import signals  # noqa: F401
