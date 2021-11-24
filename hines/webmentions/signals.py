from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import IncomingWebmention


@receiver(post_save, sender=IncomingWebmention)
@receiver(post_delete, sender=IncomingWebmention)
def incoming_webmention_actions(sender, instance, using, **kwargs):
    """
    If we're saving/deleting an incoming webmention, we need to make sure the parent
    object's incoming_webmention_count is still accurate.
    """
    instance.set_parent_incoming_webmention_data()
