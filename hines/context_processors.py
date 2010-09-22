def aggregator_context(request):
    from django.conf import settings
    from django.contrib.sites.models import Site
    from aggregator.models import Aggregator
    from weblog.models import Blog
    
    return {
        'date_format_long': settings.DATE_FORMAT_LONG,
        'date_format_short': settings.DATE_FORMAT_SHORT,
        'date_format_short_strf': settings.DATE_FORMAT_SHORT_STRF,
        'date_format_month': settings.DATE_FORMAT_MONTH,
        'time_format': settings.TIME_FORMAT,
        
        'site': Site.objects.get_current(),
        'aggregator': Aggregator.objects.get_current(),
        
        'blogs': Blog.on_site.all(),
    }