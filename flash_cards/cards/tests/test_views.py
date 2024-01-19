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


class TestRevisionView(TestCase):
    def setUp(self) -> None:
        self.url = "/cards/revision"
        Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
        )

    def test_access_new_revision_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_access_new_revision_view_no_cards(self):
        Card.objects.first().delete()

        response = self.client.get(self.url)
        messages_received = [m.message for m in messages.get_messages(response.wsgi_request)]
        self.assertTrue(messages_received, ["Error, Could not find any cards"])

    def test_use_revision_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "cards/revision.html")

    def test_display_revision_form(self):
        response = self.client.get(self.url)
        self.assertIn("revision_form_id", response.content.decode())

    def test_question_in_view_context(self):
        response = self.client.get(self.url)
        self.assertEqual(
            "Quelle est la capitale de la France ?",
            response.context["question"],
        )

    def test_hidden_question_id_in_context(self):
        response = self.client.get(self.url)
        self.assertEqual(
            Card.objects.first().id,
            response.context["question_id"],
        )

    def test_post_correct_answer_and_display_success_message(self):
        post_response = self.client.post(
            self.url,
            {"answer": "Paris"},
        )
        messages_received = [m.message for m in messages.get_messages(post_response.wsgi_request)]
        self.assertTrue(messages_received, ["Congratulation !"])

    def test_post_wrong_answer_and_display_error_message(self):
        post_response = self.client.post(
            self.url,
            {"answer": "Rome"},
        )
        messages_received = [m.message for m in messages.get_messages(post_response.wsgi_request)]
        self.assertTrue(messages_received, ["You will do better next time!"])
