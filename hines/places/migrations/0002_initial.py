# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Place'
        db.create_table('places_place', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('iso', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('place_type', self.gf('django.db.models.fields.CharField')(max_length=16)),
            ('parent', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('places', ['Place'])


    def backwards(self, orm):
        
        # Deleting model 'Place'
        db.delete_table('places_place')


    models = {
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

    complete_apps = ['places']
