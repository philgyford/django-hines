import factory

from . import models


class BlockFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.Block

    slug = factory.Sequence(lambda n: 'block-%s' % n)
    title = factory.Sequence(lambda n: 'Block %s' % n)
    content = factory.Sequence(lambda n: 'The content %s.' % n)
