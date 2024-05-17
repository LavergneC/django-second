import re
from datetime import date

from flash_cards.cards.models import Card


def get_revisable_cards(user):
    return Card.objects.filter(
        revision_date__lte=date.today(),  # Less than or equal
        user=user,
    )


def check_answer(real_answer: str, user_answer) -> bool:
    """
    Ignores differences in spacing, lower/upper case and ponctuation
    """
    real_answer = real_answer.lower().replace(" ", "")
    real_answer = re.sub(r"[^\w\s]", "", real_answer)

    user_answer = user_answer.lower().replace(" ", "")
    user_answer = re.sub(r"[^\w\s]", "", user_answer)

    return real_answer == user_answer


def sorted_leaderboard(leaderboard: dict) -> dict:
    sorted_items = sorted(
        leaderboard.items(),
        key=lambda item: item[1],
    )
    return dict(reversed(sorted_items))
