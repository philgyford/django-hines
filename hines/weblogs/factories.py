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

    class Meta:
        model = models.Post

    title = factory.Sequence(lambda n: 'Post %s' % n)

    intro = factory.Sequence(lambda n: 'The intro %s.' % n)
    body = factory.Sequence(lambda n: 'The body %s.' % n)
    slug = factory.Sequence(lambda n: 'post-%s' % n)
    blog = factory.SubFactory(BlogFactory)
    author = factory.SubFactory(UserFactory)



