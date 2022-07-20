from ditto.pinboard.models import Bookmark
from django.contrib.sitemaps import Sitemap


class BookmarkSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Bookmark.public_objects.all()

    def lastmod(self, obj):
        return obj.time_modified
