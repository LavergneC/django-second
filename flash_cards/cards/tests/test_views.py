from datetime import date, timedelta

from django.contrib import messages
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from flash_cards.cards.forms import RevisionForm
from flash_cards.cards.models import Card
from flash_cards.users.tests.factories import UserFactory


class TestNewCardView(TestCase):
    def setUp(self) -> None:
        user1 = UserFactory(password="coucou")
        self.client.login(email=user1.email, password="coucou")
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
        self.assertEqual(Card.objects.first().revision_date, date.today())

    def test_cant_create_card_because_form_is_not_valid(self):
        self.post_response = self.client.post(
            "/cards/new", {"question": "Quelle est la capitale de la France ?", "answer": ""}
        )
        self.assertEqual(Card.objects.count(), 0)
        messages_received = [m.message for m in messages.get_messages(self.post_response.wsgi_request)]
        self.assertTrue(messages_received, ["Error, could not create the card"])


class TestRevisionView(TestCase):
    def setUp(self) -> None:
        user1 = UserFactory(password="coucou")
        self.client.login(email=user1.email, password="coucou")

        self.url = "/cards/revision"
        self.first_card = Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
            user=user1,
        )
        self.second_card = Card.objects.create(
            question="Quelle est la capitale des Tuvalu ?",
            answer="Funafuti",
            user=user1,
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

    def test_get_today_card_when_first_is_for_later(self):
        self.first_card.revision_date = date.today() + timedelta(days=10)
        self.first_card.save()

        response = self.client.get(self.url)
        self.assertRedirects(
            response=response,
            expected_url=reverse("cards:revision_card", kwargs={"pk": self.second_card.pk}),
        )

    def test_get_backdated_card_when_first_is_for_today(self):
        self.second_card.revision_date = date.today() + timedelta(days=-10)
        self.second_card.save()

        response = self.client.get(self.url)
        self.assertRedirects(
            response=response,
            expected_url=reverse("cards:revision_card", kwargs={"pk": self.second_card.pk}),
        )

    def test_get_the_most_backdated_card_when_all_backdated(self):
        self.first_card.revision_date = date.today() + timedelta(days=-5)
        self.second_card.revision_date = date.today() + timedelta(days=-10)

        self.first_card.save()
        self.second_card.save()

        response = self.client.get(self.url)
        self.assertRedirects(
            response=response,
            expected_url=reverse("cards:revision_card", kwargs={"pk": self.second_card.pk}),
        )

    def test_cards_fully_revised_redirect_home_and_display_message(self):
        self.first_card.revision_date = date.today() + timedelta(days=1)
        self.first_card.save()
        self.second_card.revision_date = date.today() + timedelta(days=1)
        self.second_card.save()

        response = self.client.get(self.url)

        self.assertRedirects(
            response=response,
            expected_url=reverse("home"),
        )
        messages_received = [m.message for m in messages.get_messages(response.wsgi_request)]
        self.assertTrue(messages_received, ["All cards are already revised"])

    def test_get_card_for_current_user_only(self):
        user2 = UserFactory()
        self.second_card.user = user2
        self.second_card.revision_date = date.today() - timedelta(days=1)
        self.second_card.save()

        response = self.client.get(self.url)

        self.assertRedirects(
            response=response,
            expected_url=reverse("cards:revision_card", kwargs={"pk": self.first_card.pk}),
        )


class TestRevisionCardView(TestCase):
    def setUp(self):
        user1 = UserFactory(password="coucou")
        self.client.login(email=user1.email, password="coucou")

        self.card = Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
            user=user1,
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
        user1 = UserFactory(password="coucou")
        self.client.login(email=user1.email, password="coucou")

        self.card = Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
            revision_date=date.today(),
            user=user1,
        )
        self.card2 = Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
            revision_date=date.today(),
            user=user1,
        )
        Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
            revision_date=date.today() + timedelta(days=10),
            user=user1,
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

    def test_no_more_cards_in_context_when_revision_finished(self):
        self.assertTrue(self.response.context["have_next_card"])

        response2 = self.client.post(
            path=reverse("cards:correction_card", kwargs={"pk": self.card2.pk}),
            data={"answer": "Paris"},
        )

        self.assertFalse(response2.context["have_next_card"])

    def test_message_when_revision_finished(self):
        response2 = self.client.post(
            path=reverse("cards:correction_card", kwargs={"pk": self.card2.pk}),
            data={"answer": "Paris"},
        )
        messages_received = [m.message for m in messages.get_messages(response2.wsgi_request)]
        self.assertIn("Révision terminée !", messages_received)

    def test_right_answer_updates_card_revision_date_and_time_delta(self):
        # succeded card new revison date:
        # timedelta = timedelta * 2
        # revision_date = today_date + (new)timedelta
        card = self.response.context["card"]
        self.assertEqual(card.revision_time_delta, timedelta(days=2))
        self.assertEqual(card.revision_date, date.today() + card.revision_time_delta)

    def test_wrong_answer_updates_card_revision_date_and_time_delta(self):
        response = self._post(answer="Rome")

        card_pk = response.context["card"].pk
        card = Card.objects.get(id=card_pk)

        # Failed cards should be revised tomorrow
        self.assertEqual(card.revision_date, date.today() + timedelta(days=1))

        # Failing a card reset it's time_delta to 1 day
        self.assertEqual(card.revision_time_delta, timedelta(days=1))

    def _post(self, answer: str) -> HttpResponse:
        response = self.client.post(
            path=self.url,
            data={"answer": answer},
        )
        return response


class TestUserCardCollection(TestCase):
    def setUp(self):
        user1 = UserFactory(password="coucou")
        user2 = UserFactory()

        self.card = Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
            revision_date=date.today(),
            user=user1,
            creation_date=date.today() - timedelta(days=5),
        )
        self.card1 = Card.objects.create(
            question="Quelle est la capitale de la Chine ?",
            answer="Pékin",
            revision_date=date.today(),
            user=user1,
            creation_date=date.today(),
        )
        Card.objects.create(
            question="Le foot c'est bien ?",
            answer="Oui",
            revision_date=date.today(),
            user=user2,
            creation_date=date.today(),
        )

        self.client.login(email=user1.email, password="coucou")
        self.url = reverse("cards:card_collection")
        self.response = self.client.get(self.url)

    def test_access_card_collection_view(self):
        self.assertEqual(self.response.status_code, 200)

    def test_use_card_collection_template(self):
        self.assertTemplateUsed(self.response, "cards/user_card_collection.html")

    def test_cards_are_passed_to_context_in_correct_order(self):
        cards = self.response.context["cards"]
        self.assertEqual(len(cards), 2)

        self.assertEqual(cards.first().pk, self.card.pk)
        self.assertEqual(cards.last().pk, self.card1.pk)

        self.card1.creation_date = date.today() - timedelta(days=10)
        self.card1.save()

        second_request = self.client.get(self.url)
        cards = second_request.context["cards"]
        self.assertEqual(cards.first().pk, self.card1.pk)
        self.assertEqual(cards.last().pk, self.card.pk)
