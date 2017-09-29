default_app_config = 'hines.custom_comments.apps.CustomCommentsConfig'


def get_model():
    from hines.custom_comments.models import CustomComment
    return CustomComment

def get_form():
    from hines.custom_comments.forms import CustomCommentForm
    return CustomCommentForm

