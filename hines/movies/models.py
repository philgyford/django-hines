from django.db import models
from people.models import Person
from places.models import Country
from places.fields import CountryField
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point

class Movie(models.Model):
    """
    A movie.
    """
    name = models.CharField(max_length=255, blank=False)
    year = models.PositiveSmallIntegerField(blank=True)
    imdb_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="IMDb ID",
        help_text="The ID of the movie at IMDb, eg '0103130' (note, no 'tt' required)") 
    directors = models.ManyToManyField(Person, blank=True)
    countries = models.ManyToManyField(Country)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.year)

class Cinema(models.Model):
    """
    A place where a Movie was Viewed.
    """
    name = models.CharField(max_length=255, blank=False)
    # Default to UK.
    #country = CountryField(default=23424975, blank=False)
    country = models.ForeignKey(Country, default=23424975, blank=False)
    coordinate = models.PointField()

    def __unicode__(self):
        return self.name

class Viewing(models.Model):
    """
    An occasion on which a Movie was watched.
    """
    view_date = models.DateField(blank=False)
    cost = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    movie = models.ForeignKey(Movie, blank=False)
    cinema = models.ForeignKey(Cinema, blank=False)

    def Meta(self):
        ordering = ['-view_date',]

    def __unicode__(self):
        return "%s (%s)" % (self.movie.name, self.view_date)

