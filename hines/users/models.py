from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    In case we want to customise the user in future.
    Use this rather than django.contrib.auth.models.User.
    """
    pass

