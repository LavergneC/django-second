from django.test import TestCase

from flash_cards.cards.forms import NewCardForm, RevisionForm


class TestNewCardForm(TestCase):
    def test_display_question_and_answer_fields(self):
        form = NewCardForm()
        self.assertIn('id="question_field_id"', form.as_p())
        self.assertIn('id="answer_field_id"', form.as_p())
        self.assertNotIn('id="id_revised"', form.as_p())


class TestRevisionForm(TestCase):
    def test_revision_display_answer_fields(self):
        form = RevisionForm()
        self.assertIn('id="id_answer"', form.as_p())
