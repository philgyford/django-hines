import urllib, hashlib
from django import template
from django.conf import settings
from django.contrib.sites.models import Site


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