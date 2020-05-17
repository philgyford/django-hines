# Generated by Django 2.0.1 on 2018-01-07 17:16

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ("weblogs", "0014_post_trackback_count"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="weblogs.TaggedPost",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]
