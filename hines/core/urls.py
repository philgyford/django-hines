from django.urls import path, register_converter
from django.contrib.flatpages import views as flatpages_views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

from . import converters, feeds
from . import views as core_views
from . import app_settings
from hines.custom_comments import feeds as comments_feeds


register_converter(converters.FourDigitYearConverter, "yyyy")
register_converter(converters.TwoDigitMonthConverter, "mm")
register_converter(converters.TwoDigitDayConverter, "dd")


app_name = "hines"

admin_published_comments_slug = app_settings.COMMENTS_ADMIN_PUBLISHED_FEED_SLUG
admin_not_published_comments_slug = app_settings.COMMENTS_ADMIN_NOT_PUBLISHED_FEED_SLUG


urlpatterns = [
    path("test.html", TemplateView.as_view(template_name="hines_core/test.html")),
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
        f"feeds/{admin_published_comments_slug}/rss/",
        comments_feeds.AdminPublishedCommentsFeedRSS(),
        name="admin_published_comments_feed_rss",
    ),
    path(
        f"feeds/{admin_not_published_comments_slug}/rss/",
        comments_feeds.AdminNotPublishedCommentsFeedRSS(),
        name="admin_not_public_comments_feed_rss",
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
    path("work/", flatpages_views.flatpage, {"url": "/phil/work/"}, name="about_work"),
    path(
        "timeline/",
        flatpages_views.flatpage,
        {"url": "/phil/timeline/"},
        name="timeline",
    ),
    path("feeds/", flatpages_views.flatpage, {"url": "/phil/feeds/"}, name="feeds"),
    path(
        "<yyyy:year>/<mm:month>/<dd:day>/",
        core_views.DayArchiveView.as_view(),
        name="day_archive",
    ),
]
