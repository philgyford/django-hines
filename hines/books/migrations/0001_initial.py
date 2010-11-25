# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Series'
        db.create_table('books_series', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('home_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('books', ['Series'])

        # Adding model 'Publication'
        db.create_table('books_publication', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('home_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('notes_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('isbn_uk', self.gf('django.db.models.fields.CharField')(max_length=13, blank=True)),
            ('isbn_us', self.gf('django.db.models.fields.CharField')(max_length=13, blank=True)),
            ('series', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['books.Series'], null=True, blank=True)),
        ))
        db.send_create_signal('books', ['Publication'])

        # Adding model 'Role'
        db.create_table('books_role', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['people.Person'])),
            ('publication', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['books.Publication'])),
        ))
        db.send_create_signal('books', ['Role'])

        # Adding model 'Reading'
        db.create_table('books_reading', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start_date', self.gf('django.db.models.fields.DateField')(blank=True)),
            ('start_date_granularity', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=3)),
            ('end_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('end_date_granularity', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=3)),
            ('finished', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('publication', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['books.Publication'])),
        ))
        db.send_create_signal('books', ['Reading'])


    def backwards(self, orm):
        
        # Deleting model 'Series'
        db.delete_table('books_series')

        # Deleting model 'Publication'
        db.delete_table('books_publication')

        # Deleting model 'Role'
        db.delete_table('books_role')

        # Deleting model 'Reading'
        db.delete_table('books_reading')


    models = {
        'books.publication': {
            'Meta': {'ordering': "['name']", 'object_name': 'Publication'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.Person']", 'through': "orm['books.Role']", 'symmetrical': 'False'}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn_uk': ('django.db.models.fields.CharField', [], {'max_length': '13', 'blank': 'True'}),
            'isbn_us': ('django.db.models.fields.CharField', [], {'max_length': '13', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notes_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'series': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['books.Series']", 'null': 'True', 'blank': 'True'})
        },
        'books.reading': {
            'Meta': {'object_name': 'Reading'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_date_granularity': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '3'}),
            'finished': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publication': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['books.Publication']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'blank': 'True'}),
            'start_date_granularity': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '3'})
        },
        'books.role': {
            'Meta': {'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['people.Person']"}),
            'publication': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['books.Publication']"})
        },
        'books.series': {
            'Meta': {'object_name': 'Series'},
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
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

    complete_apps = ['books']
