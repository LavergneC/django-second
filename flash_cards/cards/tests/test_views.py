from django.contrib import messages
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from flash_cards.cards.forms import RevisionForm
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
        self.assertFalse(Card.objects.first().revised)

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
        self.first_card = Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
        )
        self.second_card = Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
        )

    def test_access_new_revision_view_no_cards(self):
        Card.objects.first().delete()
        Card.objects.first().delete()

        response = self.client.get(self.url)
        messages_received = [m.message for m in messages.get_messages(response.wsgi_request)]
        self.assertTrue(messages_received, ["Error, Could not find any cards"])

    def test_access_new_revision_view_without_cards_redirect_to_home(self):
        Card.objects.first().delete()
        Card.objects.first().delete()
        response = self.client.get(self.url)

        self.assertRedirects(
            response=response,
            expected_url=reverse("home"),
        )

    def test_access_new_revision_view_with_cards_redirect_to_card_view(self):
        response = self.client.get(self.url)

        self.assertRedirects(
            response=response,
            expected_url=reverse("cards:revision_card", kwargs={"pk": self.first_card.pk}),
        )

    def test_get_not_revised_card_when_first_is_revised(self):
        self.first_card.revised = True
        self.first_card.save()

        response = self.client.get(self.url)

        self.assertRedirects(
            response=response,
            expected_url=reverse("cards:revision_card", kwargs={"pk": self.second_card.pk}),
        )

    def test_cards_fully_revised_redirect_home_and_display_message(self):
        self.first_card.revised = True
        self.first_card.save()
        self.second_card.revised = True
        self.second_card.save()

        response = self.client.get(self.url)

        self.assertRedirects(
            response=response,
            expected_url=reverse("home"),
        )
        messages_received = [m.message for m in messages.get_messages(response.wsgi_request)]
        self.assertTrue(messages_received, ["All cards are already revised"])


class TestRevisionCardView(TestCase):
    def setUp(self):
        self.card = Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
        )
        self.url = reverse("cards:revision_card", kwargs={"pk": self.card.pk})

    def test_access_new_revision_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_use_revision_card_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "cards/revision_card.html")

    def test_display_revision_form(self):
        response = self.client.get(self.url)
        self.assertIn("revision_form_id", response.content.decode())

    def test_revision_form_in_context(self):
        response = self.client.get(self.url)

        self.assertIsInstance(
            response.context["form_revision"],
            RevisionForm,
        )

    def test_card_in_view_context(self):
        response = self.client.get(self.url)
        self.assertEqual(
            self.card,
            response.context["card"],
        )

    def _post(self, answer: str) -> HttpResponse:
        response = self.client.post(
            path=self.url,
            data={"answer": answer},
        )
        return response


class TestRevisionCardCorrection(TestCase):
    def setUp(self):
        self.card = Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
        )
        self.url = reverse("cards:correction_card", kwargs={"pk": self.card.pk})
        self.response = self._post("Paris")

    def test_access_correction_view_through_post_request(self):
        self.assertEqual(self.response.status_code, 200)

    def test_refuse_access_correction_view_through_get_request(self):
        get_response = self.client.get(self.url)
        self.assertEqual(get_response.status_code, 404)

    def test_post_answer_render_correct_template(self):
        self.assertTemplateUsed(self.response, "cards/revision_correction.html")

    def test_post_correct_answer_and_display_success_message(self):
        messages_received = [m.message for m in messages.get_messages(self.response.wsgi_request)]
        self.assertEqual(messages_received, ["Congratulation !"])

    def test_post_wrong_answer_and_display_error_message(self):
        post_response = self._post(answer="Rome")
        messages_received = [m.message for m in messages.get_messages(post_response.wsgi_request)]
        self.assertEqual(messages_received, ["You will do better next time!"])

    def test_correction_display_correct_card(self):
        self.assertIn(self.card.question, self.response.content.decode())
        self.assertIn(self.card.answer, self.response.content.decode())

    def test_display_new_question_after_click_on_next_button(self):
        pass

    def _post(self, answer: str) -> HttpResponse:
        response = self.client.post(
            path=self.url,
            data={"answer": answer},
        )
        return response
