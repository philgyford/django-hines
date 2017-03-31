import factory

from . import models


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = models.User

    username = factory.Sequence(lambda n: 'user%s' % n)
    email = factory.Sequence(lambda n: 'user%s@example.org' % n)

