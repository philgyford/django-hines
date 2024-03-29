# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-28 15:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("weblogs", "0008_auto_20170428_1449"),
    ]

    operations = [
        migrations.AddField(
            model_name="blog",
            name="show_author_email_in_feed",
            field=models.BooleanField(
                default=True,
                help_text="If checked, a Post's author's email will be included in the RSS feed.",  # noqa: E501
            ),
        ),
    ]
