from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$',
        views.HomeView.as_view(), name='home'),

    url(r'^(?P<username>\w+)/(?P<hash>\w+)/$',
        views.BookmarkDetailView.as_view(), name='bookmark_detail'),
]

