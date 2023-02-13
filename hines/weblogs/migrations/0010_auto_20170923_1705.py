# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-09-23 17:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("weblogs", "0009_blog_show_author_email_in_feed"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="comment_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="post",
            name="last_comment_time",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="post",
            name="allow_comments",
            field=models.BooleanField(
                default=True,
                help_text="If true, can still be overridden by the Blog's equivalent setting, or inThe Diary of Samuel Pepys admin Django SETTINGS.",  # noqa: E501
            ),
        ),
    ]
