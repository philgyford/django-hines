# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Aggregator.amazon_id_us'
        db.add_column('aggregator_aggregator', 'amazon_id_us', self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True), keep_default=False)

        # Adding field 'Aggregator.amazon_id_gb'
        db.add_column('aggregator_aggregator', 'amazon_id_gb', self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Aggregator.amazon_id_us'
        db.delete_column('aggregator_aggregator', 'amazon_id_us')

        # Deleting field 'Aggregator.amazon_id_gb'
        db.delete_column('aggregator_aggregator', 'amazon_id_gb')


    models = {
        'aggregator.aggregator': {
            'Meta': {'object_name': 'Aggregator'},
            'akismet_api_key': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'allowed_comment_tags': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'amazon_id_gb': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'amazon_id_us': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'enable_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'remote_comments_feed_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'remote_entries_feed_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'send_comment_emails_nonpublic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'send_comment_emails_public': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
