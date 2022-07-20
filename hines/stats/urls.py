from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "stats"

urlpatterns = [
    # So that we can use the 'stats:home' url name elsewhere:
    path(r"", views.StatsView.as_view(), {"slug": "creating"}, name="home"),
    # Redirect the /stats/creating/ URL that I shared, to the home page.
    path(
        r"creating/", RedirectView.as_view(pattern_name="stats:home", permanent=False)
    ),
    path("<slug:slug>/", views.StatsView.as_view(), name="stats_detail"),
]
