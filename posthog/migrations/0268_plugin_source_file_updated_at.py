# Generated by Django 3.2.15 on 2022-10-11 09:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posthog", "0267_add_text_tiles"),
    ]

    operations = [
        migrations.AddField(
            model_name="pluginsourcefile",
            name="updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
