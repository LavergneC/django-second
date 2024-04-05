from datetime import date, timedelta

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.urls import reverse

from flash_cards.cards.forms import NewCardForm, RevisionForm
from flash_cards.cards.models import Card
from flash_cards.cards.utils import get_revisable_cards


def new_card_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = NewCardForm(request.POST)

        if form.is_valid():
            form.save(user=request.user)
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
    cards_to_revise = get_revisable_cards(request.user)

    if not len(cards_to_revise):
        if not len(Card.objects.all()):
            messages.error(request, "Error, Could not find any cards")
        else:
            messages.error(request, "All cards are already revised")
        return redirect(reverse("home"))

    return redirect(
        reverse(
            "cards:revision_card",
            kwargs={"pk": cards_to_revise.earliest("revision_date").pk},
        )
    )


def revision_card_view(request: HttpRequest, pk):
    return render(
        request,
        "cards/revision_card.html",
        context={
            "card": Card.objects.get(id=pk),
            "form_revision": RevisionForm(),
        },
    )


def correction_card_view(request: HttpRequest, pk):
    if request.method == "GET":
        return HttpResponseNotFound()

    card = Card.objects.get(id=pk)

    if card.answer == request.POST["answer"]:
        messages.success(request, "Congratulation !")
        card.revision_time_delta = card.revision_time_delta * 2
    else:
        messages.error(request, "You will do better next time!")
        card.revision_time_delta = timedelta(days=1)

    card.revision_date = date.today() + card.revision_time_delta
    card.save()

    have_next_card = get_revisable_cards(request.user).count()

    if not have_next_card:
        messages.success(request, "Révision terminée !")

    return render(
        request,
        "cards/revision_correction.html",
        context={
            "card": card,
            "have_next_card": have_next_card,
        },
    )


def card_collection_view(request: HttpRequest):
    cards = Card.objects.filter(user=request.user).order_by("creation_date")
    return render(
        request,
        "cards/user_card_collection.html",
        context={"cards": cards},
    )
