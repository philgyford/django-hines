from books.models import Publication, Reading
from shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic.date_based import archive_year
from django.template import RequestContext


def books_publication(request, publication_id):
    publication = get_object_or_404(Publication.objects.all(), pk=publication_id)
    if publication.series:
        series_publications = Publication.objects.filter(series=publication.series).exclude(pk=publication.id)
    else:
        series_publications = [] 

    return render(request, 'books/publication_detail.html', {
        'publication': publication,
        'series_publications': series_publications,
    })

def reading_archive_year(request, year):

    queryset = Reading.objects.select_related('publication', 'publication__series', )

    return archive_year(request, year, queryset, 'end_date',
        template_object_name = 'reading',
        context_processors = [RequestContext,],
        make_object_list = True,
    )


