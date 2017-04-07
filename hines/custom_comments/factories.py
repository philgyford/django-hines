import factory

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from . import models
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
    content_type = ContentType.objects.get_for_model(Post)
    site_id = Site.objects.get_current().id

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        "Set object_pk using any `post` that was passed in."
        if extracted:
            self.object_pk = extracted.pk

