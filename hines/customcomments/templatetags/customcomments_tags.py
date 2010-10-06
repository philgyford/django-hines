from django.contrib.comments.templatetags.comments import *
import urllib, hashlib
from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from weblog.models import Entry
from customcomments.models import CommentOnEntry
register = template.Library()


@register.inclusion_tag('includes/gravatar.html')
def show_gravatar(email, size=48):
    current_site = Site.objects.get_current()
    default = 'http://' + current_site.domain + settings.MEDIA_URL + 'img/gravatar_default.jpg'
    
    url = "http://www.gravatar.com/avatar.php?"
    url += urllib.urlencode({
        'gravatar_id': hashlib.md5(email).hexdigest(), 
        'default': default, 
        'size': str(size)
    })
    
    return {'gravatar': {'url': url, 'size': size}}
    


class LatestContentNode(template.Node):
    """
    TODO: This doesn't work yet.
    It currently only returns the latest comments on ALL Entries, across all Blogs.
    I *think* we need to add a blog key to CommentOnEntry, but that's been two days of pain so far.
    
    """
    def __init__(self, blog_pk, num, varname):
        self.num, self.varname = num, varname
        self.blog_pk = template.Variable(blog_pk)
        
    def render(self, context):
        context[self.varname] = CommentOnEntry.objects.for_model(Entry).filter(
            is_public=True,
            is_removed=False,
           # blog__pk=self.blog_pk.resolve(context)
        )[:self.num]
        return ''

@register.tag
def get_latest_blog_comments(parser, token):
    """
    Can be used to get the latest comments from a blog, eg:
    get_latest_blog_comments blog.pk 5 as recent_comments
    """
    bits = token.contents.split()
    if len(bits) != 5:
        raise TemplateSyntaxError, "get_latest_blog_comments tag takes exactly four arguments"
    if bits[3] != 'as':
        raise TemplateSyntaxError, "third argument to get_latest_blog_comments tag must be 'as'"
    return LatestContentNode(bits[1], bits[2], bits[4])
