from ditto.pinboard.models import Bookmark
from django.urls import reverse

from hines.core import app_settings
from hines.core.feeds import ExtendedFeed, ExtendedRSSFeed
from hines.core.utils import get_site_url


class BookmarksFeedRSS(ExtendedFeed):
    num_items = 30

    feed_type = ExtendedRSSFeed

    content_template = "links/feeds/item_content.html"

    # Getting details about the feed:

    def link(self, obj):
        return reverse("pinboard:home")

    def title(self, obj):
        return f"Recent links from {app_settings.AUTHOR_NAME}"

    def description(self, obj):
        return f"Interesting and useful links bookmarked by {app_settings.AUTHOR_NAME}"

    def items(self, obj):
        return Bookmark.public_objects.all()[: self.num_items]

    # Getting details for each Bookmark in the feed:

    def item_description(self, item):
        return item.summary

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return item.url

    def item_author_name(self, item):
        return app_settings.AUTHOR_NAME

    def item_author_email(self, item):
        return app_settings.AUTHOR_EMAIL

    def item_pubdate(self, item):
        return item.post_time

    def item_updateddate(self, item):
        return item.time_modified

    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]

    def item_guid(self, item):
        return get_site_url() + item.get_absolute_url()
