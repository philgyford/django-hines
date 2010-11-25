from books.models import Publication 
from shortcuts import render
from django.shortcuts import get_object_or_404


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

def books_reading_year(request, year):
    pass



