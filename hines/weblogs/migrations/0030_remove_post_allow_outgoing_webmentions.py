# more hines/weblogs/migrations/0030_remove_post_allow_outgoing_webmentions.py
# Generated by Django 5.1 on 2024-09-08 13:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('weblogs', '0029_alter_post_remote_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='allow_outgoing_webmentions',
        ),
    ]
