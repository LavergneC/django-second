from django import forms

from flash_cards.cards.models import Card


class NewCardForm(forms.models.ModelForm):
    class Meta:
        model = Card
        fields = (
            "question",
            "answer",
        )

        widgets = {
            "question": forms.TextInput(attrs={"id": "question_field_id"}),
            "answer": forms.TextInput(attrs={"id": "answer_field_id"}),
        }

    def save(self, user):
        card = super().save(commit=False)
        card.user = user
        card.save()

        return card


class RevisionForm(forms.Form):
    answer = forms.CharField(label="Answer", max_length=100)
