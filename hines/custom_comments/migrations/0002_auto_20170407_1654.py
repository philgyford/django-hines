# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-07 16:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('custom_comments', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customcomment',
            options={'verbose_name': 'Comment'},
        ),
    ]
