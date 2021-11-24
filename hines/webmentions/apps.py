from django.apps import AppConfig


class WebmentionsConfig(AppConfig):
    name = "hines.webmentions"
    verbose_name = "Webmentions"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import signals  # noqa: F401
