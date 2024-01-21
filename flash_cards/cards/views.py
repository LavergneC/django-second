from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from flash_cards.cards.forms import NewCardForm, RevisionForm
from flash_cards.cards.models import Card


def new_card_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = NewCardForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Card succesfully created.")
            return redirect(reverse("home"))
        else:
            messages.error(request, "Error, could not create the card")

    return render(
        request,
        "cards/new.html",
        context={"form_new_card": NewCardForm()},
    )


def revision_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        question_id = request.POST["question_id"]
        card = Card.objects.get(id=question_id)

        if card.answer == request.POST["answer"]:
            messages.success(request, "Congratulation !")
        else:
            messages.warning(request, "You will do better next time!")
        return render(
            request,
            "cards/revision_correction.html",
            context={"card": card},
        )

    if not len(Card.objects.all()):
        messages.error(request, "Error, Could not find any cards")
        return redirect(reverse("home"))

    first_card = Card.objects.first()

    return render(
        request,
        "cards/revision.html",
        context={
            "form_revision": RevisionForm(),
            "question_id": first_card.id,
            "question": first_card.question,
        },
    )
