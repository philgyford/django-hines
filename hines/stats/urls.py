from django.urls import path
from django.views.generic import RedirectView

from . import views


app_name = 'stats'

urlpatterns = [

    # Redirect /stats/ to /stats/creating/
    path(r'',
        RedirectView.as_view(pattern_name='stats:stats_home', permanent=False)),

    # So that we can use the 'stats:stats_home' url name elsewhere:
    path(r'creating/',
        views.StatsView.as_view(),
        {'slug': 'creating',},
        name='home'),

    path('<slug:slug>/',
        views.StatsView.as_view(),
        name='stats_detail'),
]
