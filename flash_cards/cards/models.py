from cmath import sqrt
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Card(models.Model):
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)
    revision_date = models.DateField(default=timezone.now)
    revision_time_delta = models.DurationField(default=timedelta(days=1))
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    creation_date = models.DateField(default=timezone.now)

    @property
    def knowledge_score(self):
        return min(10, round(2 * sqrt(self.revision_time_delta.days).real))
