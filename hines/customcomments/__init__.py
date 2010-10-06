from customcomments.models import CommentOnEntry
from customcomments.forms import CommentFormWithBlog

def get_model():
    return CommentOnEntry

def get_form():
    return CommentFormWithBlog