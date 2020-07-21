from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

import django_comments

from hines.core.feeds import ExtendedFeed, ExtendedRSSFeed
from hines.core.utils import get_site_url


class CommentsFeedRSS(ExtendedFeed):
    """
    Public feed of recent comments across all Blogs.

    Some bits based on
    https://github.com/django/django-contrib-comments/blob/master/django_comments/feeds.py  # noqa: E501
    """

    # Is this feed showing public comments or not-public ones?
    show_public_comments = True

    feed_type = ExtendedRSSFeed

    # Used for the content:encoded element:
    content_template = "comments/feeds/content.html"

    # Getting details about the feed/site:

    def get_object(self, request):
        return Site.objects.get_current()

    def link(self, obj):
        return get_site_url()

    def title(self, obj):
        return f"Comments on {obj.name}"

    def description(self, obj):
        return f"The most recent comments on {obj.name}"

    def items(self, obj):
        site = Site.objects.get_current()
        qs = django_comments.get_model().objects.filter(
            site__pk=site.pk, is_public=self.show_public_comments, is_removed=False
        )
        return qs.order_by("-submit_date")[:20]

    # Getting details for each post in the feed:

    def item_link(self, item):
        obj = self._get_parent_object(item)
        return obj.get_absolute_url_with_domain() + f"#c{item.pk}"

    def item_pubdate(self, item):
        return item.submit_date

    def item_title(self, item):
        obj = self._get_parent_object(item)
        return f"{item.user_name}: {obj.title_text}"

    def item_author_name(self, item):
        return item.user_name

    def item_description(self, item):
        """
        I tried several things to get CDATA stuff working like we
        do with content:encoded, but everything ended up as encoded
        HTML (&lt; etc). Given the spec says "entity-encoded HTML is
        allowed" now we just put the comment's HTML in, which will get
        encoded, without using CDATA.

        Also, fyi, we're putting the full comment here, as well as in
        content:encoded, because we don't have a meaningful way to
        provide a summary of the full comment here, which is what
        we'd otherwise use description for.
        """
        return self.get_item_content(item)

    def _get_parent_object(self, item):
        # Get the object that this CustomComment was posted on:
        content_type = ContentType.objects.get(pk=item.content_type_id)
        if not content_type.model_class():
            raise AttributeError(
                "Content type %(ct_id)s object has no associated model"
                % {"ct_id": item.content_type_id}
            )
        obj = content_type.get_object_for_this_type(pk=item.object_pk)
        return obj


class AdminPublishedCommentsFeedRSS(CommentsFeedRSS):
    """
    The same as the public Comments RSS feed, except with added links
    to Remove comments.
    """

    # Is this feed showing public comments or not-public ones?
    show_public_comments = True

    content_template = "comments/feeds/content_admin_published.html"

    def title(self, obj):
        title = super().title(obj)
        return f"{title} (Admin)"

    def description(self, obj):
        description = super().description(obj)
        return f"{description} (Admin)"


class AdminNotPublicCommentsFeedRSS(CommentsFeedRSS):
    """
    The same as the Adin Published feed, except it only includes
    comments marked as is_public=False. They've probably been
    automatically marked as likely spam.

    The template gives the user the option to "delete" them, i.e. mark
    them as is_rmoved=True
    """

    # Is this feed showing public comments or not-public ones?
    show_public_comments = False

    content_template = "comments/feeds/content_admin_not_public.html"

    def title(self, obj):
        return f"Spam comments on {obj.name} (Admin)"

    def description(self, obj):
        return f"The most recent spam comments on {obj.name} (Admin)"
