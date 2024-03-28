from django.test import TestCase

from flash_cards.cards.forms import NewCardForm, RevisionForm
from flash_cards.users.tests.factories import UserFactory


class TestNewCardForm(TestCase):
    def test_display_question_and_answer_fields(self):
        form = NewCardForm()
        self.assertIn('id="question_field_id"', form.as_p())
        self.assertIn('id="answer_field_id"', form.as_p())

    def test_save_with_card_owner(self):
        form = NewCardForm(
            data={
                "question": "question",
                "answer": "answer",
            }
        )
        user = UserFactory()
        card = form.save(user=user)
        self.assertEqual(card.user, user)


class TestRevisionForm(TestCase):
    def test_revision_display_answer_fields(self):
        form = RevisionForm()
        self.assertIn('id="id_answer"', form.as_p())
