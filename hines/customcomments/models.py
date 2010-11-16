from django.db import models
from django.contrib.comments.models import Comment
from django.contrib.comments.managers import CommentManager
from aggregator.models import Aggregator
#from weblog.models import Blog

class CommentOnEntry(Comment):
    """
    Wrapping the default Comment class for comments posted to blog Entries. 
    Lets us tie each Comment to a particular Blog, which makes some things -- like lists of Comments on a Blog -- much easier.
    """
    #blog = models.ForeignKey(Blog)
    #title = models.CharField(max_length=200)
    
    objects = CommentManager()



from django.contrib.comments.signals import comment_was_posted


from django.utils.encoding import smart_str
from django.conf import settings
from django.contrib.sites.models import Site

def spam_check_comment(sender, comment, request, **kwargs):
    """
    Filter comments using TypePad AntiSpam or Akismet.
    If typepad_antispam_api_key is set in the Aggregator model, we use that.
    If it's not, and akismet_api_key is set, we use that.
    From http://sciyoshi.com/blog/2008/aug/27/using-akismet-djangos-new-comments-framework/ and
    'Practical Django Projects' 2nd edition.
    """
    # spam checking can be enabled/disabled per the comment's target Model
    #if comment.content_type.model_class() != Entry:
    #    return

    try:
        from akismet import Akismet
    except:
        return

    current_aggregator = Aggregator.objects.get_current()
    
    if not current_aggregator.test_comments_for_spam:
        # Only continue testing if the spam test is switched on.
        return

    if current_aggregator.typepad_antispam_api_key:
        # Use TypePad's AntiSpam if the key is specified.
        ak = Akismet(
            key=current_aggregator.typepad_antispam_api_key,
            blog_url='http://%s/' % Site.objects.get_current().domain
        )
        ak.baseurl = 'api.antispam.typepad.com/1.1/'
    elif current_aggregator.akismet_api_key:
        # Or use Akismet if the key is there.
        ak = Akismet(
            key=current_aggregator.akismet_api_key,
            blog_url='http://%s/' % Site.objects.get_current().domain
        )
    else:
        # Otherwise, no spam filtering.
        return

    if ak.verify_key():
        data = {
            'user_ip': comment.ip_address,
            'comment_type': 'comment',
            'comment_author': comment.user_name.encode('utf-8'),
        }
        if comment.user_url:
            data['comment_author_url'] = comment.user_url
        # When run from a unit test there was no refererer or user_agent.
        try:
            data['referrer'] = request.META['HTTP_REFERER']
        except:
            data['referrer'] = ''
        try:
            data['user_agent'] = request.META['HTTP_USER_AGENT']
        except:
            data['user_agent'] = ''

        if ak.comment_check(smart_str(comment.comment), data=data, build_data=True):
            if hasattr(comment.content_object,'author'):
                user = comment.content_object.author
            else:
                from django.contrib.auth.models import User
                user = User.objects.filter(is_superuser=True)[0]
            comment.flags.create(
                user=user,
                flag='spam'
            )
            comment.is_public = False
            comment.save()

# The dispatch_uid bit stops it being called twice for some reason.
comment_was_posted.connect(
    spam_check_comment,
    sender=CommentOnEntry,
    dispatch_uid='comments.post_comment',
)
