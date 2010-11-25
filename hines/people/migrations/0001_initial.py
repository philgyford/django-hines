# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Person'
        db.create_table('people_person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('middle_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('suffix', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
        ))
        db.send_create_signal('people', ['Person'])


    def backwards(self, orm):
        
        # Deleting model 'Person'
        db.delete_table('people_person')


    models = {
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

    complete_apps = ['people']
