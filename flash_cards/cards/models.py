from django.db import models
from django.utils import timezone


class Card(models.Model):
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)
    revision_date = models.DateField(default=timezone.now)
    revised = models.BooleanField(default=False)
