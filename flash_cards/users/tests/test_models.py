from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model

from flash_cards.cards.models import Card

User = get_user_model()


def test_user_get_absolute_url(user: User):
    assert user.get_absolute_url() == f"/users/{user.pk}/"


@pytest.mark.django_db
def test_user_leaderboard_score():
    test_user = User()
    test_user.save()
    assert test_user.leaderboard_score == 0

    first_card = Card(
        question="random question?", answer="random answer", revision_time_delta=timedelta(days=16), user=test_user
    )
    first_card.save()
    assert test_user.leaderboard_score == 8

    second_card = Card(
        question="random question 2?", answer="random answer 2", revision_time_delta=timedelta(days=32), user=test_user
    )
    second_card.save()
    assert test_user.leaderboard_score == 18

    new_user = User(email="random@example.fr")
    new_user.save()
    third_card = Card(
        question="random question 3?", answer="random answer 3", revision_time_delta=timedelta(days=32), user=new_user
    )
    third_card.save()
    assert test_user.leaderboard_score == 18
    assert new_user.leaderboard_score == 10
