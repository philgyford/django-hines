# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Publication.isbn_uk'
        db.delete_column('books_publication', 'isbn_uk')

        # Adding field 'Publication.isbn_gb'
        db.add_column('books_publication', 'isbn_gb', self.gf('django.db.models.fields.CharField')(max_length=13, null=True, blank=True), keep_default=False)

        # Changing field 'Publication.isbn_us'
        db.alter_column('books_publication', 'isbn_us', self.gf('django.db.models.fields.CharField')(max_length=13, null=True))

        # Changing field 'Publication.notes_url'
        db.alter_column('books_publication', 'notes_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True))

        # Changing field 'Publication.home_url'
        db.alter_column('books_publication', 'home_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True))


    def backwards(self, orm):
        
        # Adding field 'Publication.isbn_uk'
        db.add_column('books_publication', 'isbn_uk', self.gf('django.db.models.fields.CharField')(default='', max_length=13, blank=True), keep_default=False)

        # Deleting field 'Publication.isbn_gb'
        db.delete_column('books_publication', 'isbn_gb')

        # Changing field 'Publication.isbn_us'
        db.alter_column('books_publication', 'isbn_us', self.gf('django.db.models.fields.CharField')(max_length=13))

        # Changing field 'Publication.notes_url'
        db.alter_column('books_publication', 'notes_url', self.gf('django.db.models.fields.URLField')(max_length=200))

        # Changing field 'Publication.home_url'
        db.alter_column('books_publication', 'home_url', self.gf('django.db.models.fields.URLField')(max_length=200))


    models = {
        'books.publication': {
            'Meta': {'ordering': "['name']", 'object_name': 'Publication'},
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['people.Person']", 'through': "orm['books.Role']", 'symmetrical': 'False'}),
            'home_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isbn_gb': ('django.db.models.fields.CharField', [], {'max_length': '13', 'null': 'True', 'blank': 'True'}),
            'isbn_us': ('django.db.models.fields.CharField', [], {'max_length': '13', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'notes_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
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
