from ditto.flickr.factories import AccountFactory as FlickrAccountFactory
from ditto.flickr.factories import PhotoFactory, UserFactory
from ditto.pinboard.factories import AccountFactory as PinboardAccountFactory
from ditto.pinboard.factories import BookmarkFactory
from django.test import TestCase

from hines.core.recent import RecentObjects
from hines.core.utils import make_datetime
from hines.weblogs.factories import BlogFactory, DraftPostFactory, LivePostFactory
from hines.weblogs.models import Post


class RecentObjectsTestCase(TestCase):

    # INIT ERRORS

    def test_raises_error_with_no_kinds(self):
        with self.assertRaises(ValueError):
            RecentObjects(())

    def test_raises_error_with_invalid_format(self):
        "Error if a kind doesn't have a kind_id"
        kinds = (("fail",),)
        with self.assertRaises(ValueError):
            RecentObjects(kinds)

    def test_raises_error_with_invalid_kind(self):
        kinds = (("fail", "bob"),)
        with self.assertRaises(ValueError):
            RecentObjects(kinds)

    def test_raises_error_with_invalid_blog(self):
        # 'blog_posts' is correct but there's no Blog with a slug of 'bill':
        kinds = (("blog_posts", "bob"),)
        with self.assertRaises(ValueError):
            RecentObjects(kinds)

    def test_raises_error_with_invalid_flickr_account(self):
        # 'flickr_photos' is correct but there's no Flickr Account with a User
        # with an NSID of '12345678901@N01':
        kinds = (("flickr_photos", "12345678901@N01"),)
        with self.assertRaises(ValueError):
            RecentObjects(kinds)

    def test_raises_error_with_invalid_pinboard_account(self):
        # 'pinboard_links' is correct but there's no Pinboard Account with a
        # username of 'bob'.
        kinds = (("pinboard_links", "bob"),)
        with self.assertRaises(ValueError):
            RecentObjects(kinds)

    # GET_OBJECTS NUM

    def test_get_objects_num_default(self):
        "It should return 10 objects by default"
        b = BlogFactory(slug="my-blog")
        LivePostFactory.create_batch(11, blog=b)
        r = RecentObjects((("blog_posts", "my-blog"),))
        self.assertEqual(len(r.get_objects()), 10)

    def test_get_objects_num_custom(self):
        "It should return the defined num of objects"
        b = BlogFactory(slug="my-blog")
        LivePostFactory.create_batch(4, blog=b)
        r = RecentObjects((("blog_posts", "my-blog"),))
        self.assertEqual(len(r.get_objects(num=3)), 3)

    # BLOG POSTS

    def test_blog_posts(self):
        "It only returns Live Posts from the correct Blog"
        b1 = BlogFactory(slug="my-blog")
        b2 = BlogFactory(slug="other-blog")
        LivePostFactory.create_batch(3, blog=b1)

        # These shouldn't be returned:
        DraftPostFactory(blog=b1)
        LivePostFactory(blog=b2)

        r = RecentObjects((("blog_posts", "my-blog"),))
        objects = r.get_objects()

        self.assertEqual(len(objects), 3)

        for obj in objects:
            self.assertEqual(obj["object"].blog, b1)
            self.assertEqual(obj["object"].status, Post.Status.LIVE)

    def test_blog_posts_format(self):
        "The returned blog post dicts should be the correct format"
        blog = BlogFactory(slug="my-blog")
        post = LivePostFactory(blog=blog)
        r = RecentObjects((("blog_posts", "my-blog"),))
        objects = r.get_objects()

        self.assertEqual(objects[0]["kind"], "blog_post")
        self.assertEqual(objects[0]["object"], post)
        self.assertEqual(objects[0]["time"], post.time_published)

    # FLICKR PHOTOS

    def test_flickr_photos(self):
        "It only returns Public Photos from the correct User"
        u1 = UserFactory(nsid="11111111111@N01")
        u2 = UserFactory(nsid="22222222222@N01")
        FlickrAccountFactory(user=u1)
        FlickrAccountFactory(user=u2)

        PhotoFactory.create_batch(3, user=u1, is_private=False)

        # These shouldn't be returned:
        PhotoFactory(user=u1, is_private=True)
        PhotoFactory(user=u2, is_private=False)

        r = RecentObjects((("flickr_photos", u1.nsid),))
        objects = r.get_objects()

        self.assertEqual(len(objects), 1)

        for obj in objects:
            self.assertEqual(obj["objects"][0].user, u1)
            self.assertFalse(obj["objects"][0].is_private)

    def test_flickr_photos_several(self):
        "It should return all Photos from each day."

        user = UserFactory(nsid="11111111111@N01")
        FlickrAccountFactory(user=user)

        PhotoFactory.create_batch(
            4,
            user=user,
            is_private=False,
            post_time=make_datetime("2017-05-01 12:30:00"),
        )

        PhotoFactory.create_batch(
            3,
            user=user,
            is_private=False,
            post_time=make_datetime("2017-06-01 12:30:00"),
        )

        r = RecentObjects((("flickr_photos", user.nsid),))
        objects = r.get_objects()

        self.assertEqual(len(objects), 2)
        self.assertEqual(len(objects[0]["objects"]), 3)
        self.assertEqual(len(objects[1]["objects"]), 4)

    def test_flickr_photos_format(self):
        "The returned flickr photo dicts should be in the correct format"
        user = UserFactory(nsid="11111111111@N01")
        FlickrAccountFactory(user=user)
        photo = PhotoFactory(
            user=user, is_private=False, post_time=make_datetime("2017-05-01 12:30:00")
        )

        r = RecentObjects((("flickr_photos", user.nsid),))
        objects = r.get_objects()

        self.assertEqual(objects[0]["kind"], "flickr_photos")
        self.assertEqual(objects[0]["objects"][0], photo)
        self.assertEqual(objects[0]["time"], make_datetime("2017-05-01 00:00:00"))

    # PINBOARD BOOKMARKS

    def test_pinboard_bookmarks(self):
        "It only returns public Bookmarks from the correct Account"
        a1 = PinboardAccountFactory(username="bob")
        a2 = PinboardAccountFactory(username="terry")
        BookmarkFactory.create_batch(3, account=a1, is_private=False)

        # These shouldn't be returned:
        BookmarkFactory(account=a1, is_private=True)
        BookmarkFactory(account=a2, is_private=False)

        r = RecentObjects((("pinboard_bookmarks", "bob"),))
        objects = r.get_objects()

        self.assertEqual(len(objects), 3)

        for obj in objects:
            self.assertEqual(obj["object"].account, a1)
            self.assertFalse(obj["object"].is_private)

    def test_pinboard_bookmarks_format(self):
        "The returned bookmark dicts should be the correct format"
        account = PinboardAccountFactory(username="bob")
        bookmark = BookmarkFactory(account=account, is_private=False)
        r = RecentObjects((("pinboard_bookmarks", "bob"),))
        objects = r.get_objects()

        self.assertEqual(objects[0]["kind"], "pinboard_bookmark")
        self.assertEqual(objects[0]["object"], bookmark)
        self.assertEqual(objects[0]["time"], bookmark.post_time)

    # MIXED OBJECTS

    def test_mixture(self):
        "It should return a mixture of objects, in the correct order."

        blog = BlogFactory(slug="my-blog")
        post = LivePostFactory(
            blog=blog, time_published=make_datetime("2017-06-01 00:00:00")
        )

        flickr_user = UserFactory(nsid="11111111111@N01")
        FlickrAccountFactory(user=flickr_user)
        photo = PhotoFactory(
            user=flickr_user,
            is_private=False,
            post_time=make_datetime("2017-05-01 00:00:00"),
        )

        pinboard_account = PinboardAccountFactory(username="bob")
        bookmark = BookmarkFactory(
            account=pinboard_account,
            is_private=False,
            post_time=make_datetime("2017-07-01 00:00:00"),
        )

        kinds = (
            ("blog_posts", "my-blog"),
            ("flickr_photos", "11111111111@N01"),
            ("pinboard_bookmarks", "bob"),
        )

        objects = RecentObjects(kinds).get_objects()

        # Should be most recent first:
        self.assertEqual(objects[0]["object"], bookmark)
        self.assertEqual(objects[1]["object"], post)
        self.assertEqual(objects[2]["objects"][0], photo)
