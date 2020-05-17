from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class PagesSitemap(Sitemap):
    """
    Misc pages not included in other Sitemaps.
    """
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return [
            'home',
            'photos:home',
            'pinboard:home',
        ]

    def location(self, item):
        return reverse(item)
