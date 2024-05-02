from datetime import timedelta

import factory
import factory.fuzzy
from django.contrib.contenttypes.models import ContentType
from mentions.models import Webmention

from hines.core.utils import datetime_now
from hines.users.factories import UserFactory

from . import models


class BlogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Blog

    name = factory.Sequence(lambda n: f"Blog {n}")
    short_name = factory.Sequence(lambda n: f"Blog {n}")
    slug = factory.Sequence(lambda n: f"blog-{n}")
    sort_order = factory.Sequence(lambda n: n)


class PostFactory(factory.django.DjangoModelFactory):
    """
    Probably clearer to use either DraftPostFactory or LivePostFactory.
    """

    class Meta:
        model = models.Post

    title = factory.Sequence(lambda n: f"Post {n}")

    intro = factory.Sequence(lambda n: f"The intro {n}.")
    body = factory.Sequence(lambda n: f"The body {n}.")
    slug = factory.Sequence(lambda n: f"post-{n}")
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
    title = factory.Sequence(lambda n: f"Trackback {n}")
    excerpt = factory.fuzzy.FuzzyText(length=150)
    url = factory.Sequence(lambda n: f"http://exmple.org/{n}.html")
    ip_address = "123.123.123.123"
    blog_name = factory.Sequence(lambda n: f"Other Blog {n}")


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

    source_url = factory.Sequence(lambda n: f"http://exmple.org/{n}.html")
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
