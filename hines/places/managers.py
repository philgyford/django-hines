from django.db import models

class CountriesManager(models.Manager):
    """
    For returning just a list of Countries.
    """

    def get_query_set(self):
        return super(CountriesManager, self).get_query_set().filter(
            place_type='Country'
        )

