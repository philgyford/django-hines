from django.apps import AppConfig


class StatsConfig(AppConfig):
    name = "hines.stats"
    label = "hines_stats"
    verbose_name = "Stats"
    default_auto_field = "django.db.models.BigAutoField"
