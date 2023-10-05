# Generated by Django 3.2.19 on 2023-10-05 22:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posthog", "0352_auto_20230926_1833"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterUniqueTogether(
                    name="messagingrecord",
                    unique_together={("email_hash", "campaign_key", "campaign_count")},
                ),
            ],
            database_operations=[
                migrations.AddField(
                    model_name="organization",
                    name="never_drop_data",
                    field=models.BooleanField(blank=True, default=False, null=True),
                ),
            ],
        ),
    ]
