from datetime import date, timedelta

from django.test import TestCase

from flash_cards.cards.models import Card
from flash_cards.users.tests.factories import UserFactory


class TestCardModel(TestCase):
    def test_create_a_card(self):
        user = UserFactory()
        Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
            user=user,
        )

        self.assertEqual(Card.objects.count(), 1)
        self.assertEqual(Card.objects.first().question, "Quelle est la capitale de la France ?")
        self.assertEqual(Card.objects.first().answer, "Paris")
        self.assertEqual(Card.objects.first().revision_date, date.today())
        self.assertEqual(Card.objects.first().revision_time_delta, timedelta(days=1))
        self.assertEqual(Card.objects.first().user, user)
        self.assertEqual(Card.objects.first().creation_date, date.today())
