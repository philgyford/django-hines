from django.db import models
from django.db.models import Q 

class PublicationManager(models.Manager):

    def in_progress(self):
        """
        Gets Publications that have started being read but have not yet been finished.
        (Where by "finished" I mean stopped, rather than completed.)
        """
        return super(PublicationManager, self).get_query_set().filter(
            reading__start_date__isnull=False,
            reading__end_date__isnull=True,
        ).select_related('series',).distinct()

    def unread(self):
        """
        Gets Publications that have not yet been read or even started to be read.
        """
        return super(PublicationManager, self).get_query_set().filter(
            reading__isnull=True,
        ).select_related('series',).distinct()

    def read_on_day(self, reading_date):
        """
        Gets Publications that were being read on a particular day.
        reading_date is a date object.
        """
        return super(PublicationManager, self).get_query_set().filter(
            Q(reading__end_date__gte=reading_date) | Q(reading__end_date__isnull=True),
            reading__start_date__lte=reading_date,
        ).select_related('series',)

class ReadingManager(models.Manager):

    def years(self):
        """
        Gets all the years on which Readings have taken place.
        """
        return super(ReadingManager, self).get_query_set().dates(
            'end_date', 'year', order='ASC',
        )
