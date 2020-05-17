# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-31 16:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("weblogs", "0002_auto_20170330_1706"),
    ]

    operations = [
        migrations.RenameField(model_name="post", old_name="user", new_name="author",),
        migrations.AlterField(
            model_name="post",
            name="body_html",
            field=models.TextField(
                blank=True,
                editable=False,
                help_text="Fully HTML version of Body, created on save",
                verbose_name="Body HTML",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="html_format",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, "No formatting"),
                    (1, "Convert line breaks"),
                    (2, "Markdown"),
                ],
                default=2,
                verbose_name="HTML format",
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="intro_html",
            field=models.TextField(
                blank=True,
                editable=False,
                help_text="Fully HTML version of the Intro, created on save",
                verbose_name="Intro HTML",
            ),
        ),
    ]
