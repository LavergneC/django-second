from django.urls import path

from flash_cards.cards.views import new_card_view

app_name = "cards"

urlpatterns = [path("new", new_card_view, name="new")]
