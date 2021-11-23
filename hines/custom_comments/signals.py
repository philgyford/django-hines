from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from django_comments.signals import comment_was_posted

from .models import CustomComment
from .spam_checker import test_comment_for_spam


@receiver(post_save, sender=CustomComment)
@receiver(post_delete, sender=CustomComment)
def custom_comment_actions(sender, instance, using, **kwargs):
    """
    If we're saving/deleting a comment, we need to make sure the parent object's
    comment_count and last_comment_time are still accurate.
    """
    instance.set_parent_comment_data()


# Test a comment for Spam when it's been posted.
comment_was_posted.connect(
    test_comment_for_spam, sender=CustomComment, dispatch_uid="comments.post_comment"
)
