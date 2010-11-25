# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Movie'
        db.create_table('movies_movie', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('year', self.gf('django.db.models.fields.PositiveSmallIntegerField')(blank=True)),
            ('imdb_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('movies', ['Movie'])

        # Adding M2M table for field directors on 'Movie'
        db.create_table('movies_movie_directors', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('movie', models.ForeignKey(orm['movies.movie'], null=False)),
            ('person', models.ForeignKey(orm['people.person'], null=False))
        ))
        db.create_unique('movies_movie_directors', ['movie_id', 'person_id'])

        # Adding model 'Cinema'
        db.create_table('movies_cinema', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('country', self.gf('django_countries.fields.CountryField')(default='GB', max_length=2)),
            ('coordinate', self.gf('django.contrib.gis.db.models.fields.PointField')()),
        ))
        db.send_create_signal('movies', ['Cinema'])

        # Adding model 'Viewing'
        db.create_table('movies_viewing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('view_date', self.gf('django.db.models.fields.DateField')(blank=True)),
            ('cost', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=5, decimal_places=2, blank=True)),
            ('movie', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['movies.Movie'])),
            ('cinema', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['movies.Cinema'])),
        ))
        db.send_create_signal('movies', ['Viewing'])


    def backwards(self, orm):
        
        # Deleting model 'Movie'
        db.delete_table('movies_movie')

        # Removing M2M table for field directors on 'Movie'
        db.delete_table('movies_movie_directors')

        # Deleting model 'Cinema'
        db.delete_table('movies_cinema')

        # Deleting model 'Viewing'
        db.delete_table('movies_viewing')


    models = {
        'movies.cinema': {
            'Meta': {'object_name': 'Cinema'},
            'coordinate': ('django.contrib.gis.db.models.fields.PointField', [], {}),
            'country': ('django_countries.fields.CountryField', [], {'default': "'GB'", 'max_length': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'movies.movie': {
            'Meta': {'object_name': 'Movie'},
            'directors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.Person']", 'symmetrical': 'False'}),
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
            'view_date': ('django.db.models.fields.DateField', [], {'blank': 'True'})
        },
        'people.person': {
            'Meta': {'ordering': "['last_name', 'first_name', 'middle_name', 'suffix']", 'object_name': 'Person'},
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        }
    }

    complete_apps = ['movies']
