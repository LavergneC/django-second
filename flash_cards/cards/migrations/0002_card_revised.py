# Generated by Django 4.2.8 on 2024-02-15 21:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cards", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="card",
            name="revised",
            field=models.BooleanField(default=False),
        ),
    ]