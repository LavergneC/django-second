from django import forms

from flash_cards.cards.models import Card


class NewCardForm(forms.models.ModelForm):
    class Meta:
        model = Card
        fields = "__all__"

        widgets = {
            "question": forms.TextInput(attrs={"id": "question_field_id"}),
            "answer": forms.TextInput(attrs={"id": "answer_field_id"}),
        }
