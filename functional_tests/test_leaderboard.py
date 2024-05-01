from datetime import timedelta

from selenium.webdriver.common.by import By

from flash_cards.cards.models import Card
from flash_cards.users.tests.factories import UserFactory
from functional_tests.functional_test import FunctionalTest


class TestUserLogin(FunctionalTest):
    def setUp(self):
        super().setUp()
        super().login()

        # Cards for current user
        Card.objects.create(
            question="Quel est la capital de la Lettonie",
            answer="Riga",
            revision_time_delta=timedelta(days=2),
            user=self.user,
        )
        Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
            revision_time_delta=timedelta(days=8),
            user=self.user,
        )

        # Create a new (really good) user with his cards
        self.best_user = UserFactory()
        Card.objects.create(
            question="Quelle est la capitale de l'Italie ?",
            answer="Rome",
            revision_time_delta=timedelta(days=100),
            user=self.user,
        )
        Card.objects.create(
            question="Qui fût le 9ème César ?",
            answer="Vitellius",
            revision_time_delta=timedelta(days=64),
            user=self.user,
        )

        # Create a last (bad) user with his cards
        self.worst_user = UserFactory()
        Card.objects.create(
            question="Qui fût le premier César ?",
            answer="César",
            revision_time_delta=timedelta(days=1),
            user=self.user,
        )
        Card.objects.create(
            question="Quelle hauteur fait la tour eiffel ? (en mètre)",
            answer="330",
            revision_time_delta=timedelta(days=1),
            user=self.user,
        )
        Card.objects.create(
            question="Quelle largeur fait la tour eiffel ? (en mètre)",
            answer="124",
            revision_time_delta=timedelta(days=2),
            user=self.user,
        )

    def test_user_checks_leaderboard(self):
        # the user arrive on the website and clicks "Leaderboard"
        self.browser.get(self.live_server_url)
        self.assertTrue(self.wait_page("Maison"))
        self.browser.find_element(By.ID, "leaderboard-link").click()

        # he gets the LeaderBoard page and table
        self.assertTrue(self.wait_page("LeaderBoard"))

        # He can see users scores ranked
        table = self.browser.find_element(By.ID, "leader-board_table_id")
        rows = table.find_elements_by_tag_name("tr")

        expected_rows = ("Username", "Score", "TBD", "TBD")

        self.assertEqual(rows, expected_rows)
