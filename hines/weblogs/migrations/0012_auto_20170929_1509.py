# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-29 15:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("weblogs", "0011_trackback"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="trackback", options={"ordering": ["-time_created"]},
        ),
    ]
