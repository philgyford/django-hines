# Generated by Django 3.2.9 on 2021-11-29 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webmentions', '0006_auto_20211127_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incomingwebmention',
            name='source_url',
            field=models.URLField(blank=True, help_text='Source address of the HTTP request that sent this webmention.', verbose_name='Source URL'),
        ),
        migrations.AlterField(
            model_name='incomingwebmention',
            name='target_url',
            field=models.URLField(blank=True, help_text='URL of the object on this site that the mention was sent to.', verbose_name='Target URL'),
        ),
        migrations.AlterField(
            model_name='outgoingwebmention',
            name='source_url',
            field=models.URLField(blank=True, help_text='ULR of the object on this site that sent the webmention.', verbose_name='Source URL'),
        ),
        migrations.AlterField(
            model_name='outgoingwebmention',
            name='target_endpoint_url',
            field=models.URLField(blank=True, help_text='The endpoint URL to which we sent the webmention.', null=True, verbose_name='Target endpoint URL'),
        ),
        migrations.AlterField(
            model_name='outgoingwebmention',
            name='target_url',
            field=models.URLField(blank=True, help_text='The URL that was mentioned.', verbose_name='Target URL'),
        ),
    ]
