from datetime import date

from flash_cards.cards.models import Card


def get_revisable_cards(user):
    return Card.objects.filter(
        revision_date__lte=date.today(),  # Less than or equal
        user=user,
    )
