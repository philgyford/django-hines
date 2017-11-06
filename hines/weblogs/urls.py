from django.conf.urls import url

from . import feeds, views


urlpatterns = [
    url(
        regex=r'^post-tag-autocomplete/$',
        view=views.PostTagAutocomplete.as_view(),
        name='post_tag_autocomplete',
    ),

    url(
        regex=r"^(?P<blog_slug>[^/]+)/$",
        view=views.BlogDetailView.as_view(),
        name='blog_detail'
    ),
    url(
        regex=r"^(?P<blog_slug>[^/]+)/archive/$",
        view=views.BlogArchiveView.as_view(),
        name='blog_archive'
    ),
    url(
        regex=r"^(?P<blog_slug>[^/]+)/feeds/posts/rss/$",
        view=feeds.BlogPostsFeedRSS(),
        name='blog_feed_posts_rss'
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
