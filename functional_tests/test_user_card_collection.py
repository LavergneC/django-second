from datetime import date, timedelta

from django.utils.timezone import now
from selenium.webdriver.common.by import By

from flash_cards.cards.models import Card
from functional_tests.functional_test import FunctionalTest


class TestUserCardCollection(FunctionalTest):
    def setUp(self):
        super().setUp()
        self.login()

        Card.objects.create(
            question="Quel est la capitale de la Lettonie",
            answer="Riga",
            revision_date=now() + timedelta(days=8),
            user=self.user,
            creation_date=date(day=1, month=5, year=2020),
        )
        Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
            revision_date=now() + timedelta(weeks=24),
            user=self.user,
            creation_date=date(day=1, month=5, year=2020),
        )
        Card.objects.create(
            question="Qui fût le 9ème César ?",
            answer="Vitellius",
            revision_date=now() + timedelta(days=2),
            user=self.user,
            creation_date=date(day=1, month=5, year=2024),
        )

    def test_user_checks_on_his_card_collection(self):
        # the user arrive on the website and clicks the card list buttion
        self.browser.get(self.live_server_url)
        self.assertTrue(self.wait_page("Maison"))

        self.browser.find_element(By.ID, "card_list_button_id").click()
        self.assertTrue(self.wait_page("Ma collection"))

        # he gets all he's card, sorted by creation date
        self.fail("todo")
