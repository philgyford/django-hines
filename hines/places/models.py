from django.db import models
from managers import CountriesManager

class Place(models.Model):
    """
    Very simple Place class. 
    At the moment we only use it for getting countries.
    That's the only data we import by default.
    Could be expanded to be much bigger and better.
    IDs of each object is the WOE ID.
    """
    # Preferred local language or English place name.
    name = models.CharField(max_length = 200)
    # ISO 3166-1 country/territory code.
    iso = models.CharField(max_length = 2)
    # ISO 639-2(b) language code.
    language = models.CharField(max_length = 3)
    # Code indicating place class (eg, "Country").
    place_type = models.CharField(max_length = 16)
    # ID/WOEID of the parent object.
    parent = models.IntegerField()

    objects = models.Manager()

    class Meta:
        ordering = ['name',]

	def __unicode__(self):
		return self.name


class Country(Place):

    objects = CountriesManager()

    class Meta:
        proxy = True

    def __unicode__(self):
        return self.name

