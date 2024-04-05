from datetime import date, timedelta

from django.utils.timezone import now
from selenium.webdriver.common.by import By

from flash_cards.cards.models import Card
from flash_cards.users.tests.factories import UserFactory
from functional_tests.functional_test import FunctionalTest


class TestUserCardCollection(FunctionalTest):
    def setUp(self):
        super().setUp()
        self.login()

        user2 = UserFactory()

        self.card_1 = Card.objects.create(
            question="Quelle est la capitale de la Lettonie ?",
            answer="Riga",
            revision_date=now() + timedelta(days=8),
            user=self.user,
            creation_date=date(day=1, month=5, year=2020),
        )
        self.card_2 = Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
            revision_date=now() + timedelta(weeks=24),
            user=self.user,
            creation_date=date(day=1, month=5, year=2022),
        )
        Card.objects.create(
            question="C'est bien le foot ?",
            answer="oui",
            revision_date=now() + timedelta(days=2),
            user=user2,
            creation_date=date(day=1, month=5, year=2024),
        )

    def test_user_checks_on_his_card_collection(self):
        # the user arrive on the website and clicks the card list buttion
        self.browser.get(self.live_server_url)
        self.assertTrue(self.wait_page("Maison"))

        self.browser.find_element(By.ID, "card_list_button_id").click()
        self.assertTrue(self.wait_page("Ma collection"))

        # he gets all his cards, sorted by creation date
        card1_element = self.browser.find_element(By.ID, "id_card1")
        question = card1_element.find_element(By.ID, "id_question_field_card1").text
        self.assertEqual(question, "Quelle est la capitale de la Lettonie ?")

        card2_element = self.browser.find_element(By.ID, "id_card2")
        question = card2_element.find_element(By.ID, "id_question_field_card2").text
        self.assertEqual(question, "Quelle est la capitale de la France ?")

        # check that he doesn't get other users cards
        self.check_element_absence("id_creation_date_field_card3")

        # Each card displays it's creation and revision dates
        creation_date_str = self.card_1.creation_date.strftime("%d/%m/%Y")
        creation_date_text = card1_element.find_element(By.ID, "id_creation_date_field_card1").text
        self.assertEqual(creation_date_text, "Création : " + creation_date_str)

        creation_date_str = self.card_2.creation_date.strftime("%d/%m/%Y")
        creation_date_text = card2_element.find_element(By.ID, "id_creation_date_field_card2").text
        self.assertEqual(creation_date_text, "Création : " + creation_date_str)

        revision_date_str = self.card_1.revision_date.strftime("%d/%m/%Y")
        next_revision_date_text = card1_element.find_element(By.ID, "id_revision_date_field_card1").text
        self.assertEqual(next_revision_date_text, "Prochaine révision : " + revision_date_str)

        revision_date_str = self.card_2.revision_date.strftime("%d/%m/%Y")
        next_revision_date_text = card2_element.find_element(By.ID, "id_revision_date_field_card2").text
        self.assertEqual(next_revision_date_text, "Prochaine révision : " + revision_date_str)
