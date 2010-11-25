from django.contrib.comments.templatetags.comments import *
import urllib, hashlib
from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from weblog.models import Entry
from aggregator.models import Aggregator
from customcomments.models import CommentOnEntry
from django.template.defaultfilters import stringfilter

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
        raise TemplateSyntaxError, "%r tag takes exactly four arguments" % token.contents.split()[0]
    if bits[3] != 'as':
        raise TemplateSyntaxError, "third argument to get_latest_blog_comments tag must be 'as'"
    return LatestContentNode(bits[1], bits[2], bits[4])



@register.filter
@stringfilter
def sanitize(value):
    """
    Cleans up HTML in text (presumably contributed by a user).
    """
    from bleach import Bleach
    bl = Bleach()
    current_aggregator = Aggregator.objects.get_current()

    return bl.clean(
        value, 
        tags=current_aggregator.allowed_tags_list, 
        attributes=current_aggregator.allowed_attrs_dict
    )

    

@register.filter
@stringfilter
def linkify(value):
    """
    Wrap all http://... links in <a href... tags. 
    """
    from bleach import Bleach
    bl = Bleach()
    return bl.linkify(value, nofollow=False)


@register.filter
@stringfilter
def linkifytrunc(value, arg):
    """
    Wrap all http://... links in <a href... tags. 
    arg can be the number of characters that we'll truncate the link text to.
    """
    from bleach import Bleach

    class MyBleach(Bleach):
        """ Subclass Bleach to allow for truncating the visible link text. """
        def filter_text(self, text):
            if len(text) > arg:
                text = text[:arg] + '&#8230;' # Add ellipsis. 
            return text

    bl = MyBleach()
    return bl.linkify(value, nofollow=False)


import re
from django.template.defaultfilters import force_escape, stringfilter
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy
from django.utils.safestring import mark_safe

def autop_function(text):
    """
    Convert line breaks into <p> and <br> in an intelligent fashion.
    From: http://djangosnippets.org/snippets/349/
    """
    
    # All block level tags
    block = '(?:table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|select|form|blockquote|address|p|h[1-6])'

    # Split at <pre>, <script>, <style> and </pre>, </script>, </style> tags.
    # We don't apply any processing to the contents of these tags to avoid messing
    # up code. We look for matched pairs and allow basic nesting. For example:
    # "processed <pre> ignored <script> ignored </script> ignored </pre> processed"
    chunks = re.split(r'(?i)(</?(?:pre|script|style)[^>]*>)', text)
    # Note: PHP ensures the array consists of alternating delimiters and literals
    # and begins and ends with a literal (inserting NULL as required).
    # Also true for Python, which will insert empty strings as required.
    ignore = False
    ignoretag = ''
    output = ''
    for i, chunk in enumerate(chunks):
        if i % 2:
            # Opening or closing tag?
            open = (chunk[1] != '/')
            tag = chunk[2 - open:].split('[ >]', 2)
            if not ignore:
                if open:
                    ignore = True
                    ignoretag = tag
            # Only allow a matching tag to close it.
            elif not open and ignoretag == tag:
                ignore = False
                ignoretag = ''
        elif not ignore:
            chunk = re.sub(r'\n*$', '', chunk) + "\n\n" # just to make things a little easier, pad the end
            chunk = re.sub(r'<br />\s*<br />', r"\n\n", chunk)
            chunk = re.sub(r'(<' + block + '[^>]*>)', r"\n\1", chunk) # Space things out a little
            chunk = re.sub(r'(</' + block + '>)', r"\1\n\n", chunk) # Space things out a little
            chunk = re.sub(r"\n\n+", r"\n\n", chunk) # take care of duplicates
            chunk = re.sub(r'(?s)\n?(.+?)(?:\n\s*\n|\Z)', r"<p>\1</p>\n", chunk) # make paragraphs, including one at the end
            chunk = re.sub(r'<p>\s*</p>\n', r'', chunk) # under certain strange conditions it could create a P of entirely whitespace
            chunk = re.sub(r"<p>(<li.+?)</p>", r"\1", chunk) # problem with nested lists
            chunk = re.sub(r'(?i)<p><blockquote([^>]*)>', r"<blockquote\1><p>", chunk)
            chunk = chunk.replace('</blockquote></p>', r'</p></blockquote>')
            chunk = re.sub(r'<p>\s*(</?' + block + '[^>]*>)', r"\1", chunk)
            chunk = re.sub(r'(</?' + block + '[^>]*>)\s*</p>', r"\1", chunk)
            chunk = re.sub(r'(?<!<br />)\s*\n', r"<br />\n", chunk) # make line breaks
            chunk = re.sub(r'(</?' + block + '[^>]*>)\s*<br />', r"\1", chunk)
            chunk = re.sub(r'<br />(\s*</?(?:p|li|div|th|pre|td|ul|ol)>)', r'\1', chunk)
            chunk = re.sub(r'&([^#])(?![A-Za-z0-9]{1,8};)', r'&amp;\1', chunk)
        output += chunk
    return output

autop_function = allow_lazy(autop_function, unicode)

@register.filter
@stringfilter
def autop(value, autoescape=None):
    return mark_safe(autop_function(value))
autop.is_safe = True
autop.needs_autoescape = True
