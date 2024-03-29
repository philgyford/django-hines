from hines.core.feeds import ExtendedFeed, ExtendedRSSFeed

from .models import Blog


class BlogPostsFeedRSS(ExtendedFeed):
    num_items = 5

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
            return f"Latest posts from {obj.name}"

    def description(self, obj):
        return obj.feed_description

    def items(self, obj):
        return obj.public_posts[: self.num_items]

    # Getting details for each post in the feed:

    def item_description(self, item):
        return item.excerpt_text

    def item_title(self, item):
        return item.title_text

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

    def item_content(self, item):
        "For content:encoded"
        content = item.intro_html + item.body_html

        if item.comments_allowed or item.comment_count > 0:
            url = f"{item.get_absolute_url_with_domain()}#comments"
            text = "Read comments"
            if item.comments_allowed:
                text = f"{text} or post one"
            content += f'<hr><p><a href="{url}">{text}</a></p>'

        return content
