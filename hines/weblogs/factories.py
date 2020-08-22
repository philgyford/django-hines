from datetime import timedelta

import factory
import factory.fuzzy

from . import models
from hines.core.utils import datetime_now
from hines.users.factories import UserFactory


class BlogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Blog

    name = factory.Sequence(lambda n: "Blog %s" % n)
    short_name = factory.Sequence(lambda n: "Blog %s" % n)
    slug = factory.Sequence(lambda n: "blog-%s" % n)
    sort_order = factory.Sequence(lambda n: n)


class PostFactory(factory.django.DjangoModelFactory):
    """
    Probably clearer to use either DraftPostFactory or LivePostFactory.
    """

    class Meta:
        model = models.Post

    title = factory.Sequence(lambda n: "Post %s" % n)

    intro = factory.Sequence(lambda n: "The intro %s." % n)
    body = factory.Sequence(lambda n: "The body %s." % n)
    slug = factory.Sequence(lambda n: "post-%s" % n)
    blog = factory.SubFactory(BlogFactory)
    author = factory.SubFactory(UserFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of tags were passed in, use them.
            for tag in extracted:
                self.tags.add(tag)


class DraftPostFactory(PostFactory):
    status = models.Post.Status.DRAFT


class LivePostFactory(PostFactory):
    status = models.Post.Status.LIVE
    time_published = datetime_now()


class ScheduledPostFactory(PostFactory):
    status = models.Post.Status.SCHEDULED
    time_published = datetime_now() + timedelta(days=1)


class TrackbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Trackback

    post = factory.SubFactory(PostFactory)
    title = factory.Sequence(lambda n: "Trackback %s" % n)
    excerpt = factory.fuzzy.FuzzyText(length=150)
    url = factory.Sequence(lambda n: "http://exmple.org/%s.html" % n)
    ip_address = "123.123.123.123"
    blog_name = factory.Sequence(lambda n: "Other Blog %s" % n)
