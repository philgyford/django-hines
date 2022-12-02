from django.urls import path

from .views import index

app_name = "up"


urlpatterns = [
    path("", index, name="index"),
]
