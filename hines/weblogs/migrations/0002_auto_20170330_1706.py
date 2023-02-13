# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-30 17:06
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("weblogs", "0001_initial"),
    ]

    operations = [
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
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="status",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "Draft"), (2, "Published")], default=1
            ),
        ),
        migrations.AlterField(
            model_name="post",
            name="user",
            field=models.ForeignKey(
                default=1,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
