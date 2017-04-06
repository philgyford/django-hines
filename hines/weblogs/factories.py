import factory

from . import models
from hines.users.factories import UserFactory


class BlogFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Blog

    name = factory.Sequence(lambda n: 'Blog %s' % n)
    short_name = factory.Sequence(lambda n: 'Blog %s' % n)
    slug = factory.Sequence(lambda n: 'blog-%s' % n)
    sort_order = factory.Sequence(lambda n: n)


class PostFactory(factory.DjangoModelFactory):
    """
    Probably clearer to use either DraftPostFactory or LivePostFactory.
    """

    class Meta:
        model = models.Post

    title = factory.Sequence(lambda n: 'Post %s' % n)

    intro = factory.Sequence(lambda n: 'The intro %s.' % n)
    body = factory.Sequence(lambda n: 'The body %s.' % n)
    slug = factory.Sequence(lambda n: 'post-%s' % n)
    blog = factory.SubFactory(BlogFactory)
    author = factory.SubFactory(UserFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them.
            for tag in extracted:
                self.tags.add(tag)


class DraftPostFactory(PostFactory):
    status = models.Post.DRAFT_STATUS


class LivePostFactory(PostFactory):
    status = models.Post.LIVE_STATUS
