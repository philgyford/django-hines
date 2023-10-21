# Generated by Django 4.2.1 on 2023-10-21 10:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("weblogs", "0028_alter_post_allow_outgoing_webmentions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="remote_url",
            field=models.URLField(
                blank=True,
                help_text=(
                    "If this post is reposted from elsewhere, add the URL for the "
                    "original and it will be used for the post's permalink"
                ),
                max_length=500,
            ),
        ),
    ]