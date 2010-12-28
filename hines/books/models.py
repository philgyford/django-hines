from django.db import models
from people.models import Person
from aggregator.models import Aggregator
from managers import PublicationManager, ReadingManager


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
    def authors_names(self):
        return self.authors_names_generator(format='unlinked') 

    @property
    def authors_names_linked(self):
        return self.authors_names_generator(format='linked') 

    def authors_names_generator(self, format='unlinked'):
        """
        Returns a joined list of all the authors' full names.
        This will result in a query for each publication, so be careful if you use
        this for a list of publications...
        format is 'linked' (adds HTML links) or 'unlinked' (plain text).

        Would be nice to have this in a templatetag, but we want the non-linked
        version for the admin screens too, and I'm not sure how to satisfy both
        of those requirements.
        """
        names = []
        for role in self.role_set.select_related(depth=1):
            if format == 'unlinked':
                names.append(role.name_and_role)
            else:
                names.append(role.name_and_role_linked)
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

    objects = PublicationManager()

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
        """
        The name and role of the person, eg "Fred Bloggs (Editor)" or
        just "Fred Bloggs" if there is no role.
        """
        name_and_role = self.person.name
        return self.add_role_to_name

    @property
    def name_and_role_linked(self):
        """
        The name and role of the person, but with the name linked, eg,
        '<a href="#">Fred Bloggs</a> (Editor)'
        """
        name_and_role = '<a href="%s">%s</a>' % (self.person.get_absolute_url(), self.person.name)
        return self.add_role_to_name(name_and_role)

    def add_role_to_name(self, person_name):
        if self.name:
            person_name += ' (%s)' % self.name
        return person_name 

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

    start_date = models.DateField(blank=False, null=False)
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

    objects = ReadingManager()

    def Meta(self):
        ordering = ['-end_date', '-start_date']

    def __unicode__(self):
        return "%s (%s)" % (self.publication.name, self.start_date)

