from django.urls import path

from . import views


app_name = 'stats'

urlpatterns = [
    path(r'',
        views.HomeView.as_view(),
        name='stats_home'),

    path('<slug:slug>/',
        views.StatsView.as_view(),
        name='stats_detail'),
]
