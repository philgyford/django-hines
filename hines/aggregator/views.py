import datetime, time
from weblog.models import Blog, Entry
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response
from django.template import RequestContext


def aggregator_index(request):
    blogs = Blog.objects.with_entries(entry_limit=3)
    
    return render_to_response('aggregator/index.html', {
        'blogs': blogs,
    }, context_instance=RequestContext(request))



def aggregator_day(request, year, month, day):
    date_stamp = time.strptime(year+month+day, "%Y%m%d")
    published_date = datetime.date(*date_stamp[:3])

    blogs = Blog.objects.with_entries(
        entry_filter={
            'published_date__year' : published_date.year,
            'published_date__month' : published_date.month,
            'published_date__day' : published_date.day,
        }
    )
    
    return render_to_response('aggregator/day.html', {
        'blogs': blogs,
        'date': published_date,
    }, context_instance=RequestContext(request))

