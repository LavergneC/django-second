# Generated by Django 4.2.8 on 2024-05-02 20:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("cards", "0006_card_creation_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="card",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="cards", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
