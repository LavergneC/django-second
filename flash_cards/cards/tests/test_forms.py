from django.test import TestCase

from flash_cards.cards.forms import NewCardForm


class TestNewCardForm(TestCase):
    def test_display_question_and_answer_fields(self):
        form = NewCardForm()
        self.assertIn('id="question_field_id"', form.as_p())
        self.assertIn('id="answer_field_id"', form.as_p())
