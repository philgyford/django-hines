from people.models import Person
from books.models import Publication, Reading
from shortcuts import render
from django.shortcuts import get_object_or_404

def people_person(request, person_id):
    person = get_object_or_404(Person.objects.all(), pk=person_id)
    publication_list = person.publication_set.all()

    return render(request, 'people/person_detail.html', {
        'person': person,
        'publication_list': publication_list,
        'reading_years': Reading.objects.years(),
    })


