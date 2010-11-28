from django.db import models

class Person(models.Model):
    """
    Author of a publication, if any (journals don't usually have them, but books do).
    Director of a film.
    """
    title = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    suffix = models.CharField(max_length=12, blank=True)

    @property
    def name(self):
        parts = []
        for part in [self.title, self.first_name, self.middle_name, self.last_name, self.suffix]:
            if part:
                parts.append(part)
        return ' '.join(parts)

    @models.permalink
    def get_absolute_url(self):
        return ('people_person', [str(self.id)])

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'people'
        ordering = ['last_name', 'first_name', 'middle_name', 'suffix']
