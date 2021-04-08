from django.apps import AppConfig


class CustomCommentsConfig(AppConfig):
    name = "hines.custom_comments"
    verbose_name = "Comments"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import signals  # noqa: F401
