from datetime import date

from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
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
    avaliable_cards = Card.objects.filter(revised=False).filter(revision_date=date.today())
    card_to_revise = avaliable_cards.first()

    if not card_to_revise:
        if not len(Card.objects.all()):
            messages.error(request, "Error, Could not find any cards")
        else:
            messages.error(request, "All cards are already revised")
        return redirect(reverse("home"))

    return redirect(
        reverse(
            "cards:revision_card",
            kwargs={"pk": card_to_revise.pk},
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
    else:
        messages.error(request, "You will do better next time!")

    card.revised = True
    card.save()

    have_next_card = Card.objects.filter(revised=False).filter(revision_date=date.today()).count()

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
