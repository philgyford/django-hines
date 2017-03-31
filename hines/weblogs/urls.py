from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        regex=r"^(?P<blog_slug>[^/]+)/$",
        view=views.BlogDetailView.as_view(),
        name='blog_detail'
    ),
    url(
        regex=r"^(?P<blog_slug>[^/]+)/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<post_slug>[^/]+)/$",
        view=views.PostDetailView.as_view(),
        name='post_detail'
    ),
]
