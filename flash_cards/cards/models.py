from datetime import timedelta

from django.db import models
from django.utils import timezone


class Card(models.Model):
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)
    revision_date = models.DateField(default=timezone.now)
    revision_time_delta = models.DurationField(default=timedelta(days=1))
