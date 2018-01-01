from django.urls import path, register_converter

from hines.core import converters
from . import views


register_converter(converters.WordCharacterConverter, 'word')


app_name = 'pinboard'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    path('tags/', views.TagListView.as_view(), name='tag_list'),

    # Pinboard tags can contain pretty much any punctuation character:
    path('tags/<str:slug>/', views.TagDetailView.as_view(), name='tag_detail'),

    path('<word:username>/<word:hash>/', views.BookmarkDetailView.as_view(),
        name='bookmark_detail'),
]

