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