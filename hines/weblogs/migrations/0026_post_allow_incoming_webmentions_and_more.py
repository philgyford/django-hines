# Generated by Django 4.0.3 on 2022-03-29 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("weblogs", "0025_alter_taggedpost_tag"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="allow_incoming_webmentions",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="post",
            name="allow_outgoing_webmentions",
            field=models.BooleanField(default=False),
        ),
    ]
