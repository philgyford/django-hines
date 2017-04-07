import re

from django_comments.forms import CommentForm

from .models import CustomComment


class CustomCommentForm(CommentForm):

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return CustomComment

