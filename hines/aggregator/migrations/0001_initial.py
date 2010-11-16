# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Aggregator'
        db.create_table('aggregator_aggregator', (
            ('site', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sites.Site'], unique=True, primary_key=True)),
            ('remote_entries_feed_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('remote_comments_feed_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('enable_comments', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('aggregator', ['Aggregator'])


    def backwards(self, orm):
        
        # Deleting model 'Aggregator'
        db.delete_table('aggregator_aggregator')


    models = {
        'aggregator.aggregator': {
            'Meta': {'object_name': 'Aggregator'},
            'enable_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'remote_comments_feed_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'remote_entries_feed_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sites.Site']", 'unique': 'True', 'primary_key': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['aggregator']
