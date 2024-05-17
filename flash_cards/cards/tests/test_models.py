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
        self.assertEqual(Card.objects.first().knowledge_score, 0)

    def test_knowledge_score(self):
        card = Card.objects.create(user=UserFactory())

        # function_dict: days -> score/10
        function_dict = {1: 0, 2: 2, 4: 3, 8: 5, 16: 8, 30: 10, 32: 10, 100: 10}
        for nb_days, expected_score in function_dict.items():
            card.revision_time_delta = timedelta(days=nb_days)
            card.save()

            self.assertEqual(Card.objects.first().knowledge_score, expected_score)
