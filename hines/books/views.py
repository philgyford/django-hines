from books.models import Publication, Reading
from shortcuts import render
from django.shortcuts import get_list_or_404, get_object_or_404
from django.views.generic.date_based import archive_year
from django.template import RequestContext


def books_index(request):
    """
    Front page - listing unread and 'in progress' readings.
    """
    publications_inprogress = Publication.objects.in_progress()
    publications_unread = Publication.objects.unread()

    return render(request, 'books/index.html', {
        'publications_inprogress': publications_inprogress,
        'publications_unread': publications_unread,
        'reading_years': Reading.objects.years(),
    })


def books_publication(request, publication_id):
    """
    A single Publication, and anything else in the same series.
    """
    publication = get_object_or_404(Publication.objects.all(), pk=publication_id)
    if publication.series:
        series_publications = Publication.objects.filter(series=publication.series).exclude(pk=publication.id)
    else:
        series_publications = [] 

    return render(request, 'books/publication_detail.html', {
        'publication': publication,
        'series_publications': series_publications,
        'reading_years': Reading.objects.years(),
    })

def reading_archive_year(request, year):
    """
    Display all the Publications whose Readings were finished in a particular year.
    """
    publication_list = get_list_or_404(
        Publication.objects.filter(
            reading__end_date__year=year
        ).select_related('series',).extra(
            # A bit nasty. Can't work out how to get it to select the Reading data
            # from the reverse ForeignKey, even though it's already joining on the
            # reading table. So we're going to manually get the reading end_date, 
            # which the template needs, and just call it 'end_date'.
            select={'end_date':'books_reading.end_date'}
        ).order_by('reading__end_date')
    )

    return render(request, 'books/reading_archive_year.html', {
        'publication_list': publication_list,
        'reading_years': Reading.objects.years(),
        'year': year,
    })


