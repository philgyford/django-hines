from xml.dom import minidom

from django.utils.feedgenerator import rfc2822_date

from hines.users.factories import UserFactory
from hines.weblogs.feeds import BlogPostsFeed
from hines.weblogs.factories import BlogFactory, DraftPostFactory,\
        LivePostFactory
from tests.core import make_datetime
from tests.core.test_feeds import FeedTestCase


class BlogPostsFeedTestCase(FeedTestCase):

    def setUp(self):
        super().setUp()
        self.user = UserFactory(
                    first_name='Bob',
                    last_name='Ferris',
                    email='bob@example.org')
        self.blog = BlogFactory(
                        name='My Blog',
                        slug='my-blog',
                        feed_title='My Feed Title',
                        feed_description='My feed description.',
                        show_author_email_in_feed=True)
        # 5 older LIVE posts and then 1 new post that we test in more detail:
        posts = LivePostFactory.create_batch(5,
                            blog=self.blog,
                            time_published=make_datetime('2017-04-22 15:00:00'),
                            tags=['Dogs']
                        )
        self.post2 = LivePostFactory(
                            title='My latest post',
                            slug='my-latest-post',
                            excerpt='This is my excerpt.',
                            intro="The post intro.",
                            body="This is the post <b>body</b>.\n\nOK?",
                            author=self.user,
                            blog=self.blog,
                            time_published=make_datetime('2017-04-25 16:00:00'),
                            tags=['Fish', 'Dogs', 'Cats',]
                        )
        # These shouldn't appear in our feed:
        self.draft_post = DraftPostFactory(blog=self.blog)
        self.other_blogs_post = LivePostFactory()

    def test_response_200(self):
        response = self.client.get('/terry/my-blog/feeds/posts/')
        self.assertEqual(response.status_code, 200)


    def test_response_404(self):
        response = self.client.get('/terry/not-my-blog/feeds/posts/')
        self.assertEqual(response.status_code, 404)

    def test_feed(self):
        """
        Borrowing a lot from
        https://github.com/django/django/blob/master/tests/syndication_tests/tests.py
        """
        response = self.client.get('/terry/my-blog/feeds/posts/')
        doc = minidom.parseString(response.content)

        feed_elem = doc.getElementsByTagName('rss')
        feed = feed_elem[0]

        chan_elem = feed.getElementsByTagName('channel')
        chan = chan_elem[0]

        d = self.blog.public_posts.latest('time_modified').time_modified
        last_build_date = rfc2822_date(d)

        # We're not currently using 'ttl', 'copyright' or 'category':
        self.assertChildNodes(
            chan, [
                'title', 'link', 'description', 'language', 'lastBuildDate',
                'item', 'atom:link',
            ]
        )

        self.assertEqual(chan.attributes['xmlns:content'].value,
                        'http://purl.org/rss/1.0/modules/content/')

        self.assertChildNodeContent(chan, {
            'title': 'My Feed Title',
            'description': 'My feed description.',
            'link': 'http://127.0.0.1:8000/terry/my-blog/',
            'language': 'en-gb',
            'lastBuildDate': last_build_date,
        })

        items = chan.getElementsByTagName('item')
        self.assertEqual(len(items), 5)

        # Test the content of the most recent Post:

        self.assertChildNodeContent(items[0], {
            'title': 'My latest post',
            'description': 'This is my excerpt.',
            'link': 'http://127.0.0.1:8000/terry/my-blog/2017/04/25/my-latest-post/',
            'guid': 'http://127.0.0.1:8000/terry/my-blog/2017/04/25/my-latest-post/',
            'pubDate': rfc2822_date(self.post2.time_published),
            'author': 'bob@example.org (Bob Ferris)',
            'content:encoded': '<p>The post intro.</p><p>This is the post <b>body</b>.</p>\n<p>OK?</p>'
        })

        self.assertCategories(items[0], ['Fish', 'Dogs', 'Cats'])

        for item in items:
            self.assertChildNodes(item,
                    ['title', 'link', 'description', 'guid', 'category',
                        'pubDate', 'author', 'content:encoded',])
            # Assert that <guid> does not have any 'isPermaLink' attribute
            self.assertIsNone(item.getElementsByTagName(
                'guid')[0].attributes.get('isPermaLink'))

    def test_no_author_email(self):
        "If we don't want to show author emails, they don't appear."
        self.blog.show_author_email_in_feed = False
        self.blog.save()

        response = self.client.get('/terry/my-blog/feeds/posts/')
        doc = minidom.parseString(response.content)

        feed_elem = doc.getElementsByTagName('rss')
        feed = feed_elem[0]

        chan_elem = feed.getElementsByTagName('channel')
        chan = chan_elem[0]

        items = chan.getElementsByTagName('item')
        self.assertEqual(len(items), 5)

        # It should have a <dc:creator> instead of <author>:

        self.assertEqual(0, len( items[0].getElementsByTagName('author') ) )

        self.assertEqual(
            items[0].getElementsByTagName('dc:creator')[0].firstChild.wholeText,
            'Bob Ferris')

