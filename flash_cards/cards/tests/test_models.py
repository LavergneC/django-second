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
        self.assertEqual(Card.objects.first().knowledge_score, 1)

    def test_knowledge_score(self):
        card = Card.objects.create(user=UserFactory())

        function_dict = {1: 1, 2: 2, 4: 3, 8: 4, 16: 5, 32: 6, 64: 7, 128: 8, 256: 9, 516: 10, 1024: 10, 2048: 10}
        for key in function_dict:
            card.revision_time_delta = timedelta(days=key)
            card.save()

            self.assertEqual(Card.objects.first().knowledge_score, function_dict[key])
