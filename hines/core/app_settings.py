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

AUTHOR_NAME = getattr(settings, 'HINES_AUTHOR_NAME', '')

AUTHOR_EMAIL = getattr(settings, 'HINES_AUTHOR_EMAIL', '')

DATE_FORMAT = getattr(settings, 'HINES_DATE_FORMAT', '%-d %b %Y')

DATE_YEAR_MONTH_FORMAT = getattr(settings, 'HINES_DATE_YEAR_MONTH_FORMAT', '%b %Y')

DATETIME_FORMAT = getattr(settings, 'HINES_DATETIME_FORMAT', '[time] on [date]')

FIRST_DATE = getattr(settings, 'HINES_FIRST_DATE', False)

GOOGLE_ANALYTICS_ID = getattr(settings, 'HINES_GOOGLE_ANALYTICS_ID', '')

HOME_PAGE_DISPLAY = getattr(settings, 'HINES_HOME_PAGE_DISPLAY', {})

ROOT_DIR = getattr(settings, 'HINES_ROOT_DIR', '')

TEMPLATE_SETS = getattr(settings, 'HINES_TEMPLATE_SETS', None)

TIME_FORMAT = getattr(settings, 'HIENS_TIME_FORMAT', '%H:%M')

USE_HTTPS = getattr(settings, 'HINES_USE_HTTPS', False)
