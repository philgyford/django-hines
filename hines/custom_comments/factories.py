import factory
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django_comments.models import CommentFlag

from hines.users.factories import UserFactory
from hines.weblogs.factories import LivePostFactory
from hines.weblogs.models import Post

from . import models


class CustomCommentFactory(factory.django.DjangoModelFactory):
    """
    You can associate the comment with a Post by passing it in like this:

        p = LivePostFactory(title='My title')
        c = CustomCommentFactory(comment='hi', post=p)

    Or:
        c = CustomCommentFactory(comment='hi', content_object=p)


    Otherwise a LivePost will be created to associate this comment with.
    """

    class Meta:
        model = models.CustomComment
        exclude = ["content_object"]

    comment = factory.Sequence(lambda n: f"A comment {n}")
    site_id = Site.objects.get_current().id

    content_object = factory.SubFactory(LivePostFactory)
    object_pk = factory.SelfAttribute("content_object.pk")
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(Post)
    )

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        "Set object_pk using any `post` that was passed in."
        if extracted:
            self.content_object = extracted


class CommentFlagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentFlag

    comment = factory.SubFactory(CustomCommentFactory)
    flag = factory.Sequence(lambda n: f"Reason {n}")
    user = factory.SubFactory(UserFactory)
