from datetime import datetime
import os
import re
import sys

import pymysql.cursors
from pymysql.constants import FIELD_TYPE
from pymysql.converters import conversions as conv

from django.core.management.base import BaseCommand, CommandError

from spectator.core.models import *
from spectator.reading.models import *

# Used to import reading from the old database into the new Django one.
# Set the three environment variables for user, password and DB name.

# NOTE: This can be run over and over without it adding multiple versions of
# the same thing.

DB_USER = os.environ.get('READING_OLD_DB_USER')
DB_PASSWORD = os.environ.get('READING_OLD_DB_PASSWORD')
DB_NAME = os.environ.get('READING_OLD_DB_NAME')
DB_HOST = os.environ.get('READING_OLD_DB_HOST')
DB_PORT = os.environ.get('READING_OLD_DB_PORT')

# Set this to only fetch the first n rows from the source database, if you
# want to check things are working, with minimal possible damage:
# LIMIT = 'LIMIT 10'
LIMIT = ''

class Command(BaseCommand):

    def handle(self, *args, **options):

        # Our Reading dates in MySQL are sometimes like '2005-01-00' or
        # '2005-00-00' and pymysql will try converting these into python dates
        # which results in `None`. So we'll stop it converting them:
        new_conv = conv.copy()
        del new_conv[FIELD_TYPE.DATE]

        self.connection = pymysql.connect(host=DB_HOST,
                             user=DB_USER,
                             password=DB_PASSWORD,
                             db=DB_NAME,
                             port=DB_PORT,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor,
                             conv=new_conv)
        
        self.import_publication_series()
        self.import_publications()
        self.import_authors()
        self.import_author_publications()
        self.import_readings()

        self.connection.close()

    def import_publication_series(self):
        series_count = 0
        try:
            with self.connection.cursor() as cursor:
                sql = ("SELECT * FROM `phil_publicationseries` "
                        "ORDER BY `id` ASC {}".format(LIMIT))
                cursor.execute(sql, ())

                for series in cursor:
                    defaults = {
                        'title': series['name']
                    }
                    if series['url']:
                        defaults['url'] = series['url']

                    new_series, created = PublicationSeries.objects.update_or_create(
                                            pk=series['id'],
                                            defaults=defaults
                                        )
                    series_count += 1
        except:
            e = sys.exc_info()[0]
            raise CommandError(e)

        print("Imported {} series".format(series_count))

    def import_publications(self):
        pub_count = 0
        try:
            with self.connection.cursor() as cursor:
                sql = ("SELECT * FROM `phil_publication` "
                        "ORDER BY `id` ASC {}".format(LIMIT))
                cursor.execute(sql, ())

                for pub in cursor:

                    defaults = {
                        'title': pub['name']
                    }
                    if pub['url']:
                        defaults['official_url'] = pub['url']
                    if pub['notes_url']:
                        defaults['notes_url'] = pub['notes_url']
                    if pub['isbn_uk']:
                        defaults['isbn_uk'] = pub['isbn_uk']
                    if pub['isbn_us']:
                        defaults['isbn_us'] = pub['isbn_us']

                    if pub['publicationseries_id']:
                        try:
                            series = PublicationSeries.objects.get(pk=pub['publicationseries_id'])
                            defaults['series'] = series
                            # True for most of our things with series:
                            defaults['kind'] = 'periodical'
                        except PublicationSeries.DoesNotExist:
                            print("No PublicationSeries found with ID '{}'".format(pub['publicationseries_id']))

                    new_pub, created = Publication.objects.update_or_create(
                                            pk=pub['id'],
                                            defaults=defaults
                                        )

                    pub_count += 1
        except Exception as e:
            raise CommandError(e)

        print("Imported {} publication(s)".format(pub_count))

    def import_authors(self):
        author_count = 0

        try:
            with self.connection.cursor() as cursor:
                sql = ("SELECT * FROM `phil_author` "
                        "ORDER BY `id` ASC {}".format(LIMIT))
                cursor.execute(sql, ())

                for author in cursor:
                    names = []
                    for part in ['title', 'first_name', 'middle_name', 'last_name', 'suffix']:
                        if author[part]:
                            names.append(author[part])
                    defaults = {
                        'name': ' '.join(names)
                    }

                    new_author, created = Creator.objects.update_or_create(
                                            pk=author['id'],
                                            defaults=defaults
                                        )
                    author_count += 1
        except Exception as e:
            raise CommandError(e)

        print("Imported {} author(s)".format(author_count))

    def import_author_publications(self):
        "Connecting authors to their publications."
        ap_count = 0

        try:
            with self.connection.cursor() as cursor:
                sql = ("SELECT * FROM `phil_author_publication` "
                        "ORDER BY `id` ASC {}".format(LIMIT))
                cursor.execute(sql, ())

                for ap in cursor:
                    try:
                        publication = Publication.objects.get(pk=ap['publication_id'])
                    except Publication.DoesNotExist:
                        print("No Publication found with ID '{}'".format(ap['publication_id']))
                        continue
                    try:
                        creator = Creator.objects.get(pk=ap['author_id'])
                    except Creator.DoesNotExist:
                        print("No Creator found with ID '{}'".format(ap['author_id']))
                        continue

                    role_name = ap['role'] if ap['role'] else ''
                    PublicationRole.objects.update_or_create(
                        creator=creator,
                        publication=publication,
                        role_name=role_name
                    )
                    ap_count += 1
        except Exception as e:
            raise CommandError(e)

        print("Imported {} connection(s) between authors and publications".format(ap_count))

    def import_readings(self):
        reading_count = 0

        try:
            with self.connection.cursor() as cursor:
                sql = ("SELECT * FROM `phil_reading` "
                        "ORDER BY `id` ASC {}".format(LIMIT))
                cursor.execute(sql, ())

                for reading in cursor:
                    try:
                        publication = Publication.objects.get(pk=reading['publication_id'])
                    except Publication.DoesNotExist:
                        print("No Publication found with ID '{}'".format(reading['publication_id']))
                        continue

                    # Will be strings as we stopped pymysql converting them
                    # to date objects:
                    start_date = reading['start_date']
                    end_date = reading['end_date']

                    start_granularity = 3  # Y-m-d
                    end_granularity = 3  # Y-m-d

                    # Make dates like '2004-00-00' into '2004-01-01'.
                    # Then turn into date objects.
                    if start_date is not None:
                        if re.match('\d\d\d\d-00-00', start_date):
                            start_granularity = 6
                        elif re.match('\d\d\d\d-\d\d-00', start_date):
                            start_granularity = 4
                        
                        start_date = start_date.replace('-00', '-01')
                        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                    if end_date is not None:
                        if re.match('\d\d\d\d-00-00', end_date):
                            end_granularity = 6
                        elif re.match('\d\d\d\d-\d\d-00', end_date):
                            end_granularity = 4
                        end_date = end_date.replace('-00', '-01')
                        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

                    Reading.objects.update_or_create(
                        publication=publication,
                        start_date=start_date,
                        end_date=end_date,
                        defaults={
                            'start_granularity': start_granularity,
                            'end_granularity': end_granularity,
                            'is_finished': (reading['finished'] == 1),
                        }
                    )

                    reading_count += 1
        except Exception as e:
            raise CommandError(e)

        print("Imported {} reading(s)".format(reading_count))


