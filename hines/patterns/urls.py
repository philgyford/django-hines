from django.urls import path

from . import views


app_name = "patterns"

urlpatterns = [
    path(r"", views.PatternsView.as_view(), name="pattern_list"),
    path("<slug:slug>/", views.PatternsView.as_view(), name="pattern_detail"),
]
