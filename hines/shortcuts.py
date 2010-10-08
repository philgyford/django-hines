from django.shortcuts import render_to_response
from django.template import RequestContext

def render(request, template_name, context=None):
    '''
    Shortcut for using render_to_response with RequestContext()
    '''
    if context is None: context = {}
    return render_to_response(template_name, context,
        context_instance = RequestContext(request)
    )

def smart_truncate(text, max_length):
    '''
    Truncate some text to a certain length, splitting only after words.
    '''
    if (len(text) <= max_length):
        return text
    else:
        return text[:max_length].rsplit(' ', 1)[0]+'...'


from BeautifulSoup import BeautifulSoup, Comment
import re
from django.conf import settings

def filter_html_input_shortcut(html):
    """
    Filter, HTML. Used for user-submitted comments, before putting into the database.
    settings.ALLOWED_COMMENT_TAGS should be in form 'tag2:attr1:attr2 tag2:attr1 tag3', 
    where tags are allowed HTML tags, and attrs are the allowed attributes for that tag.
    Adapted from http://djangosnippets.org/snippets/1655/
    (Called filter_html_input_shortcut so it doesn't clash with filter_html_input
    template tag filter which then calls this function.)
    """
    allowed_tags = settings.ALLOWED_COMMENT_TAGS

    js_regex = re.compile(r'[\s]*(&#x.{1,7})?'.join(list('javascript')))
    allowed_tags = [tag.split(':') for tag in allowed_tags.split()]
    allowed_tags = dict((tag[0], tag[1:]) for tag in allowed_tags)

    soup = BeautifulSoup(html)
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        # Get rid of comments
        comment.extract()

    for tag in soup.findAll(True):
        if tag.name not in allowed_tags:
            tag.hidden = True
        else:
             # Remove javascript(?).
            tag.attrs = [(attr, js_regex.sub('', val)) for attr, val in tag.attrs
                         if attr in allowed_tags[tag.name]]

    return soup.renderContents().decode('utf8')
