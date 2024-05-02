import factory

from . import models


class BlockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Block

    slug = factory.Sequence(lambda n: f"block-{n}")
    title = factory.Sequence(lambda n: f"Block {n}")
    content = factory.Sequence(lambda n: f"The content {n}.")
