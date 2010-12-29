# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Cinema.country'
        db.delete_column('movies_cinema', 'country_id')


    def backwards(self, orm):
        
        # Adding field 'Cinema.country'
        db.add_column('movies_cinema', 'country', self.gf('django.db.models.fields.related.ForeignKey')(default=23424975, to=orm['places.Place']), keep_default=False)


    models = {
        'movies.cinema': {
            'Meta': {'object_name': 'Cinema'},
            'coordinate': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'movies.movie': {
            'Meta': {'object_name': 'Movie'},
            'countries': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['places.Place']", 'symmetrical': 'False'}),
            'directors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.Person']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imdb_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'year': ('django.db.models.fields.PositiveSmallIntegerField', [], {'blank': 'True'})
        },
        'movies.viewing': {
            'Meta': {'object_name': 'Viewing'},
            'cinema': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['movies.Cinema']"}),
            'cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'movie': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['movies.Movie']"}),
            'view_date': ('django.db.models.fields.DateField', [], {})
        },
        'people.person': {
            'Meta': {'ordering': "['last_name', 'first_name', 'middle_name', 'suffix']", 'object_name': 'Person'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        'places.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country', 'db_table': "'places_place'", '_ormbases': ['places.Place'], 'proxy': 'True'}
        },
        'places.place': {
            'Meta': {'ordering': "['name']", 'object_name': 'Place'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.IntegerField', [], {}),
            'place_type': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        }
    }

    complete_apps = ['movies']
