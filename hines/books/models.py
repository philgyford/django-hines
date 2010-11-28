from django.db import models
from people.models import Person
from aggregator.models import Aggregator


class Series(models.Model):
    """
    A series containing one or more Publications, eg 'New York Review of Books'.
    """
    name = models.CharField(max_length=255, blank=False,
        help_text="Name of the series, eg, 'New York Review of Books'")
    home_url = models.URLField(blank=True, verbose_name="URL",
        help_text="The series' website")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'series'


class Publication(models.Model):
    """
    A book or a single issue of a magazine/journal.
    """
    name = models.CharField(max_length=255, blank=False,
        help_text="Book title or name of this issue, eg, 'Vol. 22 Issue 12, December 2010'")
    home_url = models.URLField(null=True, blank=True, verbose_name="URL",
        help_text="The main URL for this book or this single issue")
    notes_url = models.URLField(null=True, blank=True, verbose_name="Notes URL",
        help_text="The URL for where your own notes, if any, live.")
    isbn_gb = models.CharField(max_length=13, null=True, blank=True, verbose_name="ISBN UK")
    isbn_us = models.CharField(max_length=13, null=True, blank=True, verbose_name="ISBN US")
    series = models.ForeignKey(Series, blank=True, null=True)
    authors = models.ManyToManyField(Person, through='Role')

    @property
    def full_name(self):
        """
        Includes the Series name, if any.
        """
        if self.series:
            return '%s: %s' % (self.series.name, self.name)
        else:
            return self.name

    @property
    def authors_names(self):
        """
        Returns a joined list of all the authors' full names.
        This will result in a query for each publication, so be careful if you use
        this for a list of publications...
        """
        names = []
        for role in self.role_set.all().select_related(depth=1):
            names.append(role.name_and_role)
        # Put commas between them, except the last pair, where you get 'and'.
        return ', '.join(names[:-2]+['']) + ' and '.join(names[-2:])

    @property
    def readings(self):
        return Reading.objects.filter(publication=self.id)


    def amazon_url(self, country):
        """
        Returns the Amazon URL for a book, if the ISBN has been set for country.
        Also adds the Affiliate ID for the country, if set in Aggregator.
        Don't call directly: use amazon_url_us or amazon_url_gb.
        """
        current_aggregator = Aggregator.objects.get_current()
        countries = {
            'gb': {
                'domain': 'co.uk',
                'isbn': self.isbn_gb,
                'amazon': current_aggregator.amazon_id_gb,
            },
            'us': {
                'domain': 'com',
                'isbn': self.isbn_us,
                'amazon': current_aggregator.amazon_id_us,
            },
        }
        if countries[country]['isbn']:
            url = 'http://www.amazon.%s/gp/product/%s/' % (
                    countries[country]['domain'], 
                    countries[country]['isbn']
                )
            if countries[country]['amazon']:
                url += '?tag='+countries[country]['amazon']
        else:
            url = ''
        return url

    @property
    def amazon_url_us(self):
        return self.amazon_url('us')

    @property
    def amazon_url_gb(self):
        return self.amazon_url('gb')

    @models.permalink
    def get_absolute_url(self):
        return ('books_publication', [str(self.id)])

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        if self.series:
            return "%s: %s" % (self.series.name, self.name)
        else:
            return self.name

class Role(models.Model):
    """
    Linking a Person to a Publication, allows an optional role, eg "Editor", "Illustrator"
    """
    name = models.CharField(max_length=30, blank=True, verbose_name='Role')
    person = models.ForeignKey(Person)
    publication = models.ForeignKey(Publication)

    @property
    def name_and_role(self):
        name_and_role = self.person.name
        if self.name:
            name_and_role += ' (%s)' % self.name
        return name_and_role

    def __unicode__(self):
        return self.name_and_role

class Reading(models.Model):
    """
    An occasion on which a publication was read (and optionally finished), between two dates.
    """
    GRANULARITY_CHOICES = (
        (3, u'Y-m-d'),
        (4, u'Y-m'),
        (6, u'Y'),
    )

    start_date = models.DateField(blank=True)
    start_date_granularity = models.PositiveSmallIntegerField(blank=False, default=3, choices=GRANULARITY_CHOICES)
    end_date = models.DateField(blank=True, null=True)
    end_date_granularity = models.PositiveSmallIntegerField(blank=False, default=3, choices=GRANULARITY_CHOICES)
    finished = models.BooleanField(blank=True, help_text="Was the complete publication read?")
    publication = models.ForeignKey(Publication, blank=False)

    @property
    def read_but_unfinished(self):
        """
        If this book has been read (ie, has an end_date) but hasn't been finished, returns True.
        """
        if self.end_date and not self.finished:
            return True
        else:
            return False


    def Meta(self):
        ordering = ['-end_date', '-start_date']

    def __unicode__(self):
        return "%s (%s)" % (self.publication.name, self.start_date)

