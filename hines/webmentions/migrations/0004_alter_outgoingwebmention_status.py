# Generated by Django 3.2.9 on 2021-11-26 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webmentions', '0003_alter_outgoingwebmention_response_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outgoingwebmention',
            name='status',
            field=models.CharField(choices=[('WA', 'Waiting to be sent'), ('UN', 'Target URL is unreachable'), ('TE', 'Target URL returned an error'), ('EE', 'Endpoint URL returned an error'), ('NE', 'No endpoint found'), ('OK', 'Target accepted the webmention')], default='WA', max_length=2),
        ),
    ]
