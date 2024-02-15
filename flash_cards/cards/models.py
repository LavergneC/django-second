from django.db import models


class Card(models.Model):
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)
    revised = models.BooleanField(default=False)
