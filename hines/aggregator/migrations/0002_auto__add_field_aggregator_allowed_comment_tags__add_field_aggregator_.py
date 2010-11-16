# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Aggregator.allowed_comment_tags'
        db.add_column('aggregator_aggregator', 'allowed_comment_tags', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True), keep_default=False)

        # Adding field 'Aggregator.test_comments_for_spam'
        db.add_column('aggregator_aggregator', 'test_comments_for_spam', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Aggregator.typepad_antispam_api_key'
        db.add_column('aggregator_aggregator', 'typepad_antispam_api_key', self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True), keep_default=False)

        # Adding field 'Aggregator.akismet_api_key'
        db.add_column('aggregator_aggregator', 'akismet_api_key', self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Aggregator.allowed_comment_tags'
        db.delete_column('aggregator_aggregator', 'allowed_comment_tags')

        # Deleting field 'Aggregator.test_comments_for_spam'
        db.delete_column('aggregator_aggregator', 'test_comments_for_spam')

        # Deleting field 'Aggregator.typepad_antispam_api_key'
        db.delete_column('aggregator_aggregator', 'typepad_antispam_api_key')

        # Deleting field 'Aggregator.akismet_api_key'
        db.delete_column('aggregator_aggregator', 'akismet_api_key')


    models = {
        'aggregator.aggregator': {
            'Meta': {'object_name': 'Aggregator'},
            'akismet_api_key': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'allowed_comment_tags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'enable_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'remote_comments_feed_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'remote_entries_feed_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sites.Site']", 'unique': 'True', 'primary_key': 'True'}),
            'test_comments_for_spam': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'typepad_antispam_api_key': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['aggregator']
