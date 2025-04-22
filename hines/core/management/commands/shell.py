from django.core.management.commands import shell
from django.db.models import __all__ as models_all


class Command(shell.Command):
    def get_auto_imports(self):
        """Automatically import more useful things"
        via https://adamj.eu/tech/2025/04/07/django-whats-new-5.2/
        """
        return super().get_auto_imports() + [
            "os",
            "pathlib.Path",
            "re",
            "sys",
            "django.conf.settings",
            "django.urls.resolve",
            "django.urls.reverse",
            # Everything from django.db.models
            *[f"django.db.models.{name}" for name in models_all],
        ]
