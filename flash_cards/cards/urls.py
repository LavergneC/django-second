from django.urls import path

from flash_cards.cards.views import (
    card_collection_view,
    correction_card_view,
    new_card_view,
    revision_card_view,
    revision_view,
)

app_name = "cards"

urlpatterns = [
    path("new", new_card_view, name="new"),
    path("card_collection", card_collection_view, name="card_collection"),
    path("revision", revision_view, name="revision"),
    path("revision/<int:pk>", revision_card_view, name="revision_card"),
    path("revision/<int:pk>/correction", correction_card_view, name="correction_card"),
]
