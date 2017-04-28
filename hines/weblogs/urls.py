from django.conf.urls import url

from . import views
from . import feeds


urlpatterns = [
    url(
        regex=r"^(?P<blog_slug>[^/]+)/$",
        view=views.BlogDetailView.as_view(),
        name='blog_detail'
    ),
    url(
        regex=r"^(?P<blog_slug>[^/]+)/feed/$",
        view=feeds.BlogPostsFeed(),
        name='blog_feed'
    ),
    url(
        regex=r"^(?P<blog_slug>[^/]+)/tags/$",
        view=views.BlogTagListView.as_view(),
        name='blog_tag_list'
    ),
    url(
        regex=r"^(?P<blog_slug>[^/]+)/tags/(?P<tag_slug>[^/]+)/$",
        view=views.BlogTagDetailView.as_view(),
        name='blog_tag_detail'
    ),
    url(
        regex=r"^(?P<blog_slug>[^/]+)/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<post_slug>[^/]+)/$",
        view=views.PostDetailView.as_view(),
        name='post_detail'
    ),
    url(
        regex=r"^(?P<blog_slug>[^/]+)/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$",
        view=views.PostDayArchiveView.as_view(),
        name='post_day_archive'
    ),
    url(
        regex=r"^(?P<blog_slug>[^/]+)/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$",
        view=views.PostMonthArchiveView.as_view(),
        name='post_month_archive'
    ),
    url(
        regex=r"^(?P<blog_slug>[^/]+)/(?P<year>[0-9]{4})/$",
        view=views.PostYearArchiveView.as_view(),
        name='post_year_archive'
    ),

]
