# Generated by Django 2.1.3 on 2018-12-09 17:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("weblogs", "0017_auto_20181204_1440"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="excerpt",
            field=models.TextField(
                blank=True,
                help_text="Brief summary, HTML allowed. If not set, it will be a "
                "truncated version of the Intro.",
            ),
        ),
    ]
