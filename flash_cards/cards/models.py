from datetime import date

from django.db import models


class Card(models.Model):
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)
    revision_date = models.DateField(default=date.today())
    revised = models.BooleanField(default=False)
