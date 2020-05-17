from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Trackback


@receiver(post_save, sender=Trackback)
@receiver(post_delete, sender=Trackback)
def trackback_actions(sender, instance, using, **kwargs):
    """
    If we're saving/deleting a Trackback, we need to make sure its Post's
    trackback_count is still accurate.
    """
    instance.set_parent_trackback_data()
