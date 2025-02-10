from django.urls import path

from . import views

app_name = "pinboard"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    # Pinboard tags can contain pretty much any punctuation character:
    path("tags/<str:slug>/", views.TagDetailView.as_view(), name="tag_detail"),
    path(
        "bookmark-tag-autocomplete/",
        views.BookmarkTagAutocomplete.as_view(),
        name="bookmark_tag_autocomplete",
    ),
    path(
        # These path converters are defined in config.urls:
        "<word:username>/<word:hash>/",
        views.BookmarkDetailView.as_view(),
        name="bookmark_detail",
    ),
]
