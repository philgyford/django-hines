import datetime, time
from weblog.models import Blog, Entry
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import get_list_or_404, get_object_or_404, render_to_response
from django.template import RequestContext
from taggit.models import Tag


def weblog_archive_month(request, blog_slug, year, month):
    blog = get_object_or_404(Blog, slug=blog_slug)
    date_stamp = time.strptime(year+month+'01', "%Y%m%d")
    published_date = datetime.date(*date_stamp[:3])
    entries = list(Entry.live.filter(
                                blog__slug__exact = blog_slug,
                                published_date__year = published_date.year,
                                published_date__month = published_date.month,
                            ))
    
    return render_to_response('weblog/entry_archive_month.html', {
        'blog': blog,
        'entries': entries,
        'date': published_date,
    }, context_instance=RequestContext(request))


def weblog_blog_index(request, blog_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)

    paginator = Paginator(Entry.live.filter(blog__slug__exact = blog_slug), 15, orphans=2)
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    
    # If page request (9999) is out of range, deliver last page of results.
    try:
        entries = paginator.page(page)
    except (EmptyPage, InvalidPage):
        entries = paginator.page(paginator.num_pages)
        
    return render_to_response('weblog/index.html', {
        'blog': blog,
        'entries': entries,
    }, context_instance=RequestContext(request))


def weblog_entry_detail(request, blog_slug, year, month, day, slug):
    
    date_stamp = time.strptime(year+month+day, "%Y%m%d")
    published_date = datetime.date(*date_stamp[:3])
    
    entry = get_object_or_404(Entry.live.all(),
                                blog__slug__exact = blog_slug,
                                published_date__year = published_date.year,
                                published_date__month = published_date.month,
                                published_date__day = published_date.day,
                                slug=slug,
                            )

    other_blogs = Blog.objects.with_entries(
        entry_filter={
            'published_date__year' : published_date.year,
            'published_date__month' : published_date.month,
            'published_date__day' : published_date.day,
        },
        entry_exclude={
            'pk' : entry.pk
        }
    )
    
    return render_to_response('weblog/entry_detail.html', {
        'blog': entry.blog,
        'entry': entry,
        'other_blogs': other_blogs,
    }, context_instance=RequestContext(request))


def weblog_tag(request, blog_slug, tag_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)
    tag = get_object_or_404(Tag, slug=tag_slug)
    
    entries = list(Entry.live.filter(
                                blog__slug__exact = blog.slug,
                                tags__name__in=[tag.slug]
                            ))
    
    return render_to_response('weblog/tag.html', {
        'blog': blog,
        'tag': tag,
        'entries': entries,
    }, context_instance=RequestContext(request))
