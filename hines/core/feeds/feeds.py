import re

from django.contrib.sites.models import Site
from django.urls import reverse
from mentions.models import Webmention

from hines.core import app_settings
from hines.core.recent import RecentObjects
from hines.core.utils import get_site_url

from . import ExtendedFeed, ExtendedRSSFeed


class EverythingFeedRSS(ExtendedFeed):
    """
    The feed that combines posts, bookmarks, photos into one.
    """

    num_items = 14

    feed_type = ExtendedRSSFeed

    description_template = "hines_core/feeds/everything_description.html"

    content_template = "hines_core/feeds/everything_content.html"

    # Getting details about the feed/site:

    def get_object(self, request):
        return Site.objects.get_current()

    def link(self, obj):
        return get_site_url()

    def title(self, obj):
        return "%s: Everything" % obj.name

    def description(self, obj):
        return "Things written, created, linked to or liked by Phil Gyford"

    def items(self, obj):
        kinds = app_settings.EVERYTHING_FEED_KINDS
        return RecentObjects(kinds).get_objects(num=self.num_items)

    # Getting details for each post in the feed:

    def item_title(self, item):
        if item["kind"] == "blog_post":
            title = item["object"].title_text

        elif item["kind"] == "pinboard_bookmark":
            title = "[Link] {}".format(item["object"].title)

        elif item["kind"] == "flickr_photos":
            title = "Photos from {}".format(item["time"].strftime("%-d %B %Y"))
        else:
            title = item.title

        return title

    def item_link(self, item):
        if item["kind"] == "flickr_photos":
            t = item["time"]
            return reverse(
                "hines:day_archive",
                kwargs={
                    "year": t.year,
                    "month": t.strftime("%m"),
                    "day": t.strftime("%d"),
                },
            )
        elif item["kind"] == "blog_post" and item["object"].remote_url:
            # e.g. A comment on another site; link to it there.
            return item["object"].remote_url
        elif item["kind"] == "pinboard_bookmark":
            # Link to the bookmark's URL itself, not to our permalink.
            return item["object"].url
        else:
            return item["object"].get_absolute_url()

    def item_pubdate(self, item):
        if item["kind"] == "blog_post":
            return item["object"].time_published

        elif item["kind"] == "pinboard_bookmark":
            return item["object"].post_time

        elif item["kind"] == "flickr_photos":
            return item["objects"][0].post_time

    def item_updateddate(self, item):
        if item["kind"] == "blog_post" or item["kind"] == "pinboard_bookmark":
            return item["object"].time_modified

        elif item["kind"] == "flickr_photos":
            dt = None
            for photo in item["objects"]:
                if dt is None or photo.last_update_time > dt:
                    dt = photo.last_update_time
            return dt

    def item_author_name(self, item):
        name = None
        if item["kind"] == "blog_post":
            name = item["object"].author.display_name
        elif app_settings.AUTHOR_NAME:
            name = app_settings.AUTHOR_NAME
        return name

    def item_author_email(self, item):
        email = None
        if item["kind"] == "blog_post":
            if item["object"].blog.show_author_email_in_feed:
                email = item["object"].author.email
        elif app_settings.AUTHOR_EMAIL:
            email = app_settings.AUTHOR_EMAIL
        return email


class AdminWebmentionsFeedRSS(ExtendedFeed):
    """
    Includes both public and spam comments, plus links to
    approve/delete/edit them in the Admin.

    Assumes that the target_object of a Webmention is a weblog Post
    object, that has a `title` field and a
    `get_absolute_url_with_domain()` method.
    """

    feed_type = ExtendedRSSFeed

    # This will be used in <content:encoded>
    content_template = "hines_core/feeds/webmentions_admin.html"

    # Getting details about the feed/site:

    def get_object(self, request):
        return Site.objects.get_current()

    def link(self, obj):
        return get_site_url()

    def title(self, obj):
        return f"Webmentions on {obj.name} (Admin)"

    def description(self, obj):
        return f"The most recent webmentions on {obj.name} (Admin)"

    def items(self, obj):
        """
        Because webmentions can be accepted for any URL, but we're only
        interested in those on Posts, we're ignoring all Webmentions
        that don't have a valid GenericForeignKey – they'll be ones
        to pages that aren't PostDetail pages.
        """
        return Webmention.objects.exclude(object_id__isnull=True).order_by(
            "-created_at"
        )[:10]

    # Getting details for each post in the feed:

    def item_link(self, item):
        "The #m1 fragment links to the mention on the Post's page, if published"
        return item.target_object.get_absolute_url_with_domain() + f"#m{item.pk}"

    def item_pubdate(self, item):
        return item.published

    def item_title(self, item):
        """
        For each item's title, include the title of the linked-to blog Post, followed
        by the URL that mentioned it.
        Flag as not validated, if it isn't.
        """
        url_re = re.compile(r"https?://(www\.)?")
        source_url = url_re.sub("", item.source_url)
        title = f"{item.target_object.title}: {source_url}"

        if not item.validated:
            title = f"[NOT VALIDATED] {title}"

        return title

    def item_description(self, item):
        "Return the most important thing, the admin URL for the simple description"
        return get_site_url() + reverse(
            "admin:mentions_webmention_change", args=[item.pk]
        )
