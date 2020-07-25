from django_comments.forms import CommentForm
from hcaptcha.fields import hCaptchaField

from .models import CustomComment


class CustomCommentForm(CommentForm):

    # I think that removing this is all we need to do to remove
    # the hcaptcha field from the form:
    hcaptcha = hCaptchaField()

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return CustomComment

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["name"].widget.attrs["required"] = "required"

        self.fields["email"].required = True
        self.fields["email"].widget.attrs["required"] = "required"
        self.fields["email"].help_text = "Will not be displayed."

        self.fields["url"].help_text = "e.g. Your personal website, Twitter URL, etc."

        self.fields["comment"].required = True
        self.fields["comment"].widget.attrs["required"] = "required"
