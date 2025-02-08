from django.contrib.flatpages import views as flatpages_views
from django.urls import path
from django.views.generic.base import RedirectView

from hines.custom_comments import feeds as comments_feeds

from . import app_settings, feeds
from . import views as core_views

app_name = "hines"

admin_comments_slug = app_settings.COMMENTS_ADMIN_FEED_SLUG

urlpatterns = [
    # Send anyone going to '/phil/' to the home page at '/'.
    path("", RedirectView.as_view(url="/", permanent=False)),
    # RSS FEEDS
    path(
        "feeds/everything/rss/", feeds.EverythingFeedRSS(), name="everything_feed_rss"
    ),
    path(
        "feeds/comments/rss/",
        comments_feeds.CommentsFeedRSS(),
        name="comments_feed_rss",
    ),
    path(
        f"feeds/{admin_comments_slug}/rss/",
        comments_feeds.AdminCommentsFeedRSS(),
        name="admin_comments_feed_rss",
    ),
    # Flatpages with names:
    path("about/", flatpages_views.flatpage, {"url": "/phil/about/"}, name="about"),
    path(
        "about/cv/",
        flatpages_views.flatpage,
        {"url": "/phil/about/cv/"},
        name="about_cv",
    ),
    path(
        "about/press/",
        flatpages_views.flatpage,
        {"url": "/phil/about/press/"},
        name="about_press",
    ),
    path(
        "about/projects/",
        flatpages_views.flatpage,
        {"url": "/phil/about/projects/"},
        name="about_projects",
    ),
    path(
        "about/site/",
        flatpages_views.flatpage,
        {"url": "/phil/about/site/"},
        name="about_site",
    ),
    path(
        "archive/", flatpages_views.flatpage, {"url": "/phil/archive/"}, name="archive"
    ),
    path(
        "blogroll/",
        flatpages_views.flatpage,
        {"url": "/phil/blogroll/"},
        name="blogroll",
    ),
    path("work/", flatpages_views.flatpage, {"url": "/phil/work/"}, name="about_work"),
    path(
        "timeline/",
        flatpages_views.flatpage,
        {"url": "/phil/timeline/"},
        name="timeline",
    ),
    path("feeds/", flatpages_views.flatpage, {"url": "/phil/feeds/"}, name="feeds"),
    path(
        # These path converters are defined in config.urls:
        "<yyyy:year>/<mm:month>/<dd:day>/",
        core_views.DayArchiveView.as_view(),
        name="day_archive",
    ),
    path(
        "admin-custom/clear-cache/",
        core_views.admin_clear_cache,
        name="admin_clear_cache",
    ),
]
