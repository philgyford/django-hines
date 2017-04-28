from django.contrib.syndication.views import Feed
from django.urls import reverse

from hines.core.feeds import ExtendedRSSFeed
from .models import Blog, Post


class BlogPostsFeed(Feed):
    feed_type = ExtendedRSSFeed

    # Getting details about the blog:

    def get_object(self, request, blog_slug):
        return Blog.objects.get(slug=blog_slug)

    def link(self, obj):
        return obj.get_absolute_url()

    def title(self, obj):
        if obj.feed_title:
            return obj.feed_title
        else:
            return "Latest posts from {}".format(obj.name)

    def description(self, obj):
        return obj.feed_description

    def items(self, obj):
        return obj.public_posts[:5]


    # Getting details for each post in the feed:

    def item_description(self, item):
        return item.excerpt

    def item_author_name(self, item):
        return item.author.display_name

    def item_author_email(self, item):
        if item.blog.show_author_email_in_feed:
            return item.author.email

    def item_pubdate(self, item):
        return item.time_published

    def item_updateddate(self, item):
        return item.time_modified

    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]

    def item_extra_kwargs(self, item):
        extra = super().item_extra_kwargs(item)
        extra.update({'content_encoded': self.item_content_encoded(item)})
        return extra

    def item_content_encoded(self, item):
        return item.intro_html + item.body_html

