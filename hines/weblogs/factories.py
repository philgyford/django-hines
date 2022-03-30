from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
import factory
import factory.fuzzy

from . import models
from hines.core.utils import datetime_now
from hines.users.factories import UserFactory
from mentions.models import Webmention


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


class WebmentionFactory(factory.django.DjangoModelFactory):
    """
    You can associate the incoming Webmention with a Post by passing it in like this:

        p = LivePostFactory(title='My title')
        w = WebmentionFactory(post=p)

    Or:
        w = WebmentionFactory(target_object=p)

    Otherwise a LivePost will be created to associate this webmention with.
    """

    class Meta:
        model = Webmention
        exclude = ["target_object"]

    source_url = factory.Sequence(lambda n: "http://exmple.org/%s.html" % n)
    # Not sure we can set this to anything accurate automatically:
    target_url = "/blog/post/"
    sent_by = "123.123.123.123"
    quote = factory.fuzzy.FuzzyText(length=150)

    target_object = factory.SubFactory(LivePostFactory)
    object_id = factory.SelfAttribute("target_object.pk")
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(models.Post)
    )

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        "Set object_id using any `post` that was passed in."
        if extracted:
            self.target_object = extracted
