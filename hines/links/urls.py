from django.conf.urls import url

from . import views


app_name = 'pinboard'

urlpatterns = [
    url(r'^$',
        views.HomeView.as_view(),
        name='home'),

    url(r'^tags/$',
        views.TagListView.as_view(),
        name='tag_list'
    ),

    url(r'^tags/(?P<slug>[^/]+)/$',
        views.TagDetailView.as_view(),
        name='tag_detail'
    ),

    url(r'^(?P<username>\w+)/(?P<hash>\w+)/$',
        views.BookmarkDetailView.as_view(),
        name='bookmark_detail'),
]

