import factory

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from django_comments.models import CommentFlag

from . import models
from hines.users.factories import UserFactory
from hines.weblogs.factories import PostFactory
from hines.weblogs.models import Post


class CustomCommentFactory(factory.DjangoModelFactory):
    """
    You can associate the comment with a particular Post by passing it in:

        p = LivePostFactory(title='My title')
        c = CustomCommentFactory(comment='hi', post=p)

    """

    class Meta:
        model = models.CustomComment

    comment = factory.Sequence(lambda n: 'A comment %s' % n)
    content_type_id = ContentType.objects.get_for_model(Post).pk
    site_id = Site.objects.get_current().id

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        "Set object_pk using any `post` that was passed in."
        if extracted:
            self.object_pk = extracted.pk


class CommentFlagFactory(factory.DjangoModelFactory):

    class Meta:
        model = CommentFlag

    comment = factory.SubFactory(CustomCommentFactory)
    flag = factory.Sequence(lambda n: 'Reason %s' % n)
    user = factory.SubFactory(UserFactory)


