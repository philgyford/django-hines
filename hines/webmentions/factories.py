import factory

from django.contrib.contenttypes.models import ContentType

from . import models
from hines.weblogs.factories import LivePostFactory


class IncomingWebmentionFactory(factory.django.DjangoModelFactory):
    """
    You can associate the webmention with a Post by passing it in like this:

        p = LivePostFactory(title='My title')
        c = IncomingWebmentionFactory(source_title='hi', post=p)

    Or:
        c = IncomingWebmentionFactory(source_title='hi', content_object=p)


    Otherwise a LivePost will be created to associate this comment with.
    """

    class Meta:
        model = models.IncomingWebmention
        exclude = ["content_object"]

    source_title = factory.Sequence(lambda n: "Source title %s" % n)

    source_url = factory.Faker("uri")

    content_object = factory.SubFactory(LivePostFactory)
    object_pk = factory.SelfAttribute("content_object.pk")
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        "Set object_pk using any `post` that was passed in."
        if extracted:
            self.content_object = extracted


class OutgoingWebmentionFactory(factory.django.DjangoModelFactory):
    """
    You can associate the webmention with a Post by passing it in like this:

        p = LivePostFactory(title='My title')
        c = OutgoingWebmentionFactory(target_url='https://foo.com', post=p)

    Or:
        c = OutgoingWebmentionFactory(target_url='https://foo.com', content_object=p)


    Otherwise a LivePost will be created to associate this comment with.
    """

    class Meta:
        model = models.OutgoingWebmention
        exclude = ["content_object"]

    target_url = factory.Faker("uri")

    target_endpoint_url = factory.Faker("uri")

    content_object = factory.SubFactory(LivePostFactory)
    object_pk = factory.SelfAttribute("content_object.pk")
    content_type = factory.LazyAttribute(
        lambda o: ContentType.objects.get_for_model(o.content_object)
    )

    @factory.post_generation
    def post(self, create, extracted, **kwargs):
        "Set object_pk using any `post` that was passed in."
        if extracted:
            self.content_object = extracted
