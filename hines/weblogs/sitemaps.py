from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return Post.public_objects.all()

    def lastmod(self, obj):
        return obj.time_modified

