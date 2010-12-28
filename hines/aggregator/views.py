import datetime, time
from weblog.models import Blog, Entry
from books.models import Publication
from django.shortcuts import get_list_or_404, get_object_or_404
from shortcuts import render


def aggregator_index(request):
    blogs = Blog.objects.with_entries(entry_limit=3)

    publications_inprogress = Publication.objects.in_progress()
    
    return render(request, 'aggregator/index.html', {
        'blogs': blogs,
        'publications_inprogress': publications_inprogress,
    })



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

    publications_day = Publication.objects.read_on_day(published_date)
    
    return render(request, 'aggregator/day.html', {
        'blogs': blogs,
        'date': published_date,
        'publications_day': publications_day,
    })

