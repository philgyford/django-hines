from people.models import Person
from books.models import Publication
from shortcuts import render
from django.shortcuts import get_object_or_404

def people_person(request, person_id):
    person = get_object_or_404(Person.objects.all(), pk=person_id)
    publications = person.publication_set.all()

    return render(request, 'people/person_detail.html', {
        'person': person,
        'publications': publications,
    })


