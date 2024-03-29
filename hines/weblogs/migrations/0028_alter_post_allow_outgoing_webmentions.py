# Generated by Django 4.1.3 on 2022-11-28 12:24

import mentions.models.mixins.mentionable
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("weblogs", "0027_remove_post_allow_incoming_webmentions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="allow_outgoing_webmentions",
            field=models.BooleanField(
                default=mentions.models.mixins.mentionable._outgoing_default,
                verbose_name="allow outgoing webmentions",
            ),
        ),
    ]
