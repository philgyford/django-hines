from django.conf import settings


ALLOW_COMMENTS = getattr(settings, 'HINES_ALLOW_COMMENTS', True)

COMMENTS_ALLOWED_TAGS = getattr(settings, 'HINES_COMMENTS_ALLOWED_TAGS', [
    'a',
    'abbr',
    'acronym',
    'b',
    'blockquote',
    'code',
    'em',
    'i',
    'li',
    'ol',
    'strong',
    'ul',
])

COMMENTS_ALLOWED_ATTRIBUTES = getattr(settings, 'HINES_COMMENTS_ALLOWED_ATTRIBUTES', {
    'a': ['href', 'title'],
    'acronym': ['title'],
    'abbr': ['title'],
})

FIRST_DATE = getattr(settings, 'HINES_FIRST_DATE', False)

GOOGLE_ANALYTICS_ID = getattr(settings, 'HINES_GOOGLE_ANALYTICS_ID', '')

HOME_PAGE_DISPLAY = getattr(settings, 'HINES_HOME_PAGE_DISPLAY', {})

ROOT_DIR = getattr(settings, 'HINES_ROOT_DIR', '')

TEMPLATE_SETS = getattr(settings, 'HINES_TEMPLATE_SETS', None)

USE_HTTPS = getattr(settings, 'HINES_USE_HTTPS', False)
