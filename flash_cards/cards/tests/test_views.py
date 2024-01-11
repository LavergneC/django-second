from django.contrib import messages
from django.test import TestCase

from flash_cards.cards.models import Card


class TestNewCardView(TestCase):
    def setUp(self) -> None:
        self.response = self.client.get("/cards/new")

    def test_access_new_card_view(self):
        self.assertEqual(self.response.status_code, 200)

    def test_use_new_card_template(self):
        self.assertTemplateUsed(self.response, "cards/new.html")

    def test_display_new_card_form(self):
        self.assertIn("create_card_form_id", self.response.content.decode())

    def test_create_card_object_on_post_request(self):
        self.post_response = self.client.post(
            "/cards/new", {"question": "Quelle est la capitale de la France ?", "answer": "Paris"}
        )
        self.assertEqual(Card.objects.count(), 1)
        self.assertEqual(Card.objects.first().question, "Quelle est la capitale de la France ?")
        self.assertEqual(Card.objects.first().answer, "Paris")

    def test_cant_create_card_because_form_is_not_valid(self):
        self.post_response = self.client.post(
            "/cards/new", {"question": "Quelle est la capitale de la France ?", "answer": ""}
        )
        self.assertEqual(Card.objects.count(), 0)
        messages_received = [m.message for m in messages.get_messages(self.post_response.wsgi_request)]
        self.assertTrue(messages_received, ["Error, could not create the card"])
