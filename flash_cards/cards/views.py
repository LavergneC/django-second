from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from flash_cards.cards.forms import NewCardForm


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
