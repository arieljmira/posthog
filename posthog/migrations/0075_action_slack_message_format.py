# Generated by Django 3.0.7 on 2020-08-04 14:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posthog", "0074_toolbar_default_on"),
    ]

    operations = [
        migrations.AddField(
            model_name="action",
            name="slack_message_format",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
