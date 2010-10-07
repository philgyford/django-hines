from django import template


register = template.Library()


import re
from django.template.defaultfilters import force_escape, stringfilter
from django.utils.encoding import force_unicode
from django.utils.functional import allow_lazy
from django.utils.safestring import mark_safe


def autop_function(value):
    """
    Convert line breaks into <p> and <br> in an intelligent fashion.
    From: http://greenash.net.au/thoughts/2010/05/an-autop-django-template-filter/
    Originally based on: http://photomatt.net/scripts/autop
    
    Ported directly from the Drupal _filter_autop() function:
    http://api.drupal.org/api/function/_filter_autop
    """
    
    # All block level tags
    block = '(?:table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|ul|ol|li|pre|select|form|blockquote|address|p|h[1-6]|hr)'

    # Split at <pre>, <script>, <style> and </pre>, </script>, </style> tags.
    # We don't apply any processing to the contents of these tags to avoid messing
    # up code. We look for matched pairs and allow basic nesting. For example:
    # "processed <pre> ignored <script> ignored </script> ignored </pre> processed"
    chunks = re.split('(</?(?:pre|script|style|object)[^>]*>)', value)
    ignore = False
    ignoretag = ''
    output = ''
    
    for i, chunk in zip(range(len(chunks)), chunks):
        prev_ignore = ignore
        
        if i % 2:
            # Opening or closing tag?
            is_open = chunk[1] != '/'
            tag = re.split('[ >]', chunk[2-is_open:], 2)[0]
            if not ignore:
                if is_open:
                    ignore = True
                    ignoretag = tag
            
            # Only allow a matching tag to close it.
            elif not is_open and ignoretag == tag:
                ignore = False
                ignoretag = ''
        
        elif not ignore:
            chunk = re.sub('\n*$', '', chunk) + "\n\n" # just to make things a little easier, pad the end
            chunk = re.sub('<br />\s*<br />', "\n\n", chunk)
            chunk = re.sub('(<'+ block +'[^>]*>)', r"\n\1", chunk) # Space things out a little
            chunk = re.sub('(</'+ block +'>)', r"\1\n\n", chunk) # Space things out a little
            chunk = re.sub("\n\n+", "\n\n", chunk) # take care of duplicates
            chunk = re.sub('\n?(.+?)(?:\n\s*\n|$)', r"<p>\1</p>\n", chunk) # make paragraphs, including one at the end
            chunk = re.sub("<p>(<li.+?)</p>", r"\1", chunk) # problem with nested lists
            chunk = re.sub('<p><blockquote([^>]*)>', r"<blockquote\1><p>", chunk)
            chunk = chunk.replace('</blockquote></p>', '</p></blockquote>')
            chunk = re.sub('<p>\s*</p>\n?', '', chunk) # under certain strange conditions it could create a P of entirely whitespace
            chunk = re.sub('<p>\s*(</?'+ block +'[^>]*>)', r"\1", chunk)
            chunk = re.sub('(</?'+ block +'[^>]*>)\s*</p>', r"\1", chunk)
            chunk = re.sub('(?<!<br />)\s*\n', "<br />\n", chunk) # make line breaks
            chunk = re.sub('(</?'+ block +'[^>]*>)\s*<br />', r"\1", chunk)
            chunk = re.sub('<br />(\s*</?(?:p|li|div|th|pre|td|ul|ol)>)', r'\1', chunk)
            chunk = re.sub('&([^#])(?![A-Za-z0-9]{1,8};)', r'&amp;\1', chunk)
        
        # Extra (not ported from Drupal) to escape the contents of code blocks.
        code_start = re.search('^<code>', chunk)
        code_end = re.search(r'(.*?)<\/code>$', chunk)
        if prev_ignore and ignore:
            if code_start:
                chunk = re.sub('^<code>(.+)', r'\1', chunk)
            if code_end:
                chunk = re.sub(r'(.*?)<\/code>$', r'\1', chunk)
            chunk = chunk.replace('<\\/pre>', '</pre>')
            chunk = force_escape(chunk)
            if code_start:
                chunk = '<code>' + chunk
            if code_end:
                chunk += '</code>'
        
        output += chunk
    
    return output

autop_function = allow_lazy(autop_function, unicode)

@register.filter
def autop(value, autoescape=None):
    return mark_safe(autop_function(value))
autop.is_safe = True
autop.needs_autoescape = True
autop = stringfilter(autop)