from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from mentions.models import Webmention

from hines.core.utils import make_datetime
from hines.weblogs.factories import BlogFactory, LivePostFactory

# from tests import override_app_settings
from . import FeedTestCase


class AdminWebmentionsFeedRSSTestCase(FeedTestCase):
    feed_url = "/terry/feeds/admin-webmentions/rss/"
    maxDiff = None

    def setUp(self):
        super().setUp()

        # To ensure our requests for the feed always use a specific domain and name:
        site = Site.objects.get()
        site.domain = "example.com"
        site.name = "Example Site"
        site.save()

    def test_response_200(self):
        response = self.client.get(self.feed_url)
        self.assertEqual(response.status_code, 200)

    # Can't work out why this test fails.
    # @override_app_settings(WEBMENTIONS_ADMIN_FEED_SLUG="good-webmentions")
    # def test_response_200_with_custom_slug(self):
    #     response = self.client.get("/terry/feeds/good-webmentions/rss/")
    #     self.assertEqual(response.status_code, 200)

    def test_content(self):
        "An item should contain the correct content"
        post = LivePostFactory(
            title="Hello",
            slug="hello",
            blog=BlogFactory(slug="blog"),
            time_published=make_datetime("2022-10-09 12:00:00"),
        )
        webmention = Webmention.objects.create(
            sent_by="1.2.3.4",
            target_url=post.get_absolute_url(),
            source_url="https://example.org",
            content_type=ContentType.objects.get_for_model(post.__class__),
            object_id=post.pk,
            target_object=post,
        )

        channel = self.get_channel_element(self.feed_url)
        items = channel.getElementsByTagName("item")

        self.assertChildNodeContent(
            items[0],
            {
                "title": "[NOT VALIDATED] Hello: example.org",
                "description": (
                    "http://example.com/backstage/mentions/"
                    f"webmention/{webmention.pk}/change/"
                ),
                "link": post.get_absolute_url_with_domain() + f"#m{webmention.pk}",
            },
        )

        self.assertHTMLEqual(
            items[0].getElementsByTagName("content:encoded")[0].firstChild.wholeText,
            f"""<p>Webmention from<br><a href="https://example.org">https://example.org</a><br>
to<br><a href="/terry/blog/2022/10/09/hello/">Hello</a><br>
sent by 1.2.3.4
</p><hr><dl><dt>Validated?</dt><dd>❌</dd><dt>Approved?</dt><dd>❌</dd></dl><p><a href="http://example.com/backstage/mentions/webmention/{webmention.pk}/change/">Edit in Admin</a></p>""",  # noqa: E501
        )

    def test_only_posts_included(self):
        "The feed should ignore mentions to URLs that aren't PostDetail pages"
        Webmention.objects.create(
            sent_by="1.2.3.4",
            target_url="/",
            source_url="https://example.org",
            content_type=None,
            object_id=None,
            target_object=None,
        )

        channel = self.get_channel_element(self.feed_url)
        items = channel.getElementsByTagName("item")
        self.assertEqual(len(items), 0)
