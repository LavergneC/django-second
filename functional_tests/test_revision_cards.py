from datetime import date, timedelta

from freezegun import freeze_time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from flash_cards.cards.models import Card
from flash_cards.users.tests.factories import UserFactory
from functional_tests.functional_test import FunctionalTest


class TestCardsRevision(FunctionalTest):
    def setUp(self):
        super().setUp()
        self.login()

        tomorrow = date.today() + timedelta(days=1)
        yesterday = date.today() + timedelta(days=-1)

        user2 = UserFactory(
            email="nico@example.fr",
            password="plopplop",
        )

        Card.objects.create(
            question="Quel est la capital de la Lettonie",
            answer="Riga",
            revision_date=yesterday - timedelta(days=1),
            user=user2,
        )
        Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
            revision_date=tomorrow,
            user=self.user,
        )
        Card.objects.create(
            question="Quelle est la capitale de l'Italie ?",
            answer="Rome",
            revision_date=date.today(),
            user=self.user,
        )
        Card.objects.create(
            question="Qui fût le 9ème César ?",
            answer="Vitellius",
            revision_date=yesterday,
            user=self.user,
        )
        Card.objects.create(
            question="Qui fût le premier César ?",
            answer="César",
            revision_date=tomorrow,
            user=self.user,
        )

    def get_date_string(self, date: date) -> str:
        date_str = "Prochaine révision: "
        date_str += date.strftime("%B %e, %Y")
        return date_str.replace("  ", " ")

    def test_user_do_a_revision(self):
        # the user arrive on the website
        self.browser.get(self.live_server_url)
        self.assertTrue(self.wait_page("Maison"))

        # He clicks the "start revision" button
        self.browser.find_element(By.ID, "revision_button_id").click()
        self.assertTrue(self.wait_page("Révision"))

        # He's prompted with a question from a card that should be revised in priority
        try:
            form = self.browser.find_element(By.ID, "revision_form_id")
        except NoSuchElementException:
            self.fail("Could not find question_text_id")

        self.assertTrue(self.text_in_body("Qui fût le 9ème César ?"))

        # He answer correctly
        form.find_element(By.ID, "id_answer").send_keys("vitellius .")
        # he clicks on the "check answer" button
        self.browser.find_element(By.ID, "check_answer_id").click()

        # He gets the correct answer and rewarding message
        question = self.browser.find_element(By.ID, "question_text_id").text
        answer = self.browser.find_element(By.ID, "answer_text_id").text

        self.assertEqual(question, "Qui fût le 9ème César ?")
        self.assertEqual(answer, "Vitellius")
        self.assertTrue(self.text_in_body("Congratulation !"))

        # He also gets the next revision date and the card knowledge score
        date_str = self.get_date_string(date.today() + timedelta(days=2))
        self.assertTrue(self.text_in_body(date_str))
        self.assertTrue(self.text_in_body("Maîtrise : 2/10"))

        # He clicks the next button
        self.browser.find_element(By.ID, "next_revision_button_id").click()

        # He's prompted with a new question from a created card
        try:
            form = self.browser.find_element(By.ID, "revision_form_id")
        except NoSuchElementException:
            self.fail("Could not find question_text_id")

        self.assertTrue(self.text_in_body("Quelle est la capitale de l'Italie ?"))

        # He answer uncorrectly and he clicks on the "check answer" button
        form.find_element(By.ID, "id_answer").send_keys("Paris")
        self.browser.find_element(By.ID, "check_answer_id").click()

        self.assertTrue(self.wait_page("Révision - correction"))

        # He gets the correct answer and supporting message
        question = self.browser.find_element(By.ID, "question_text_id").text
        answer = self.browser.find_element(By.ID, "answer_text_id").text

        self.assertEqual(question, "Quelle est la capitale de l'Italie ?")
        self.assertEqual(answer, "Rome")
        self.assertTrue(self.text_in_body("You will do better next time!"))

        # He also gets the next revision date and the card knowledge score
        date_str = self.get_date_string(date.today() + timedelta(days=1))
        self.assertTrue(self.text_in_body(date_str))
        self.assertTrue(self.text_in_body("Maîtrise : 0/10"))

        # Since he revised all today's cards, the next button is not available
        # and a message tells him
        try:
            self.browser.find_element(By.ID, "next_revision_button_id").click()
            self.fail("Should NOT find next button")
        except NoSuchElementException:
            pass

        self.assertTrue(self.text_in_body("Révision terminée !"))

        # he clicks on the "Finish revision" button, he's redirected to the main page
        self.browser.find_element(By.ID, "finish_revision_button_id").click()
        self.assertTrue(self.wait_page("Maison"))

    def setup_test_user_comes_back_next_day_to_do_a_revision(self):
        # the user does a classic revision; already tested in test_user_do_a_revision
        self.browser.get(self.live_server_url)
        self.wait_page("Maison")
        self.browser.find_element(By.ID, "revision_button_id").click()
        self.wait_page("Révision")

        # He answer correctly to the first card
        self.assertTrue(self.text_in_body("Qui fût le 9ème César ?"))
        form = self.browser.find_element(By.ID, "revision_form_id")
        form.find_element(By.ID, "id_answer").send_keys("Vitellius")
        self.browser.find_element(By.ID, "check_answer_id").click()

        # He clicks the next button
        self.browser.find_element(By.ID, "next_revision_button_id").click()

        # He's prompted with a new question, he's wrong this time
        self.assertTrue(self.text_in_body("Quelle est la capitale de l'Italie ?"))
        form = self.browser.find_element(By.ID, "revision_form_id")
        form.find_element(By.ID, "id_answer").send_keys("Naples")
        self.browser.find_element(By.ID, "check_answer_id").click()

    def test_user_comes_back_next_day_to_do_a_revision(self):
        # User action on the first day
        self.setup_test_user_comes_back_next_day_to_do_a_revision()

        # Card status :
        # |               Question                | revision date |    Reason     |
        # |---------------------------------------|---------------|---------------|
        # | Quelle est la capitale de la France ? | J+1           | Init value    |
        # | Qui fût le premier César ?            | J+1           | Init value    |
        # | Quelle est la capitale de l'Italie ?  | J+1           | Failed today  |
        # | Qui fût le 9ème César ?               | J+2           | Success today |

        question_pool = [
            "Quelle est la capitale de la France ?",
            "Qui fût le premier César ?",
            "Quelle est la capitale de l'Italie ?",
        ]

        # set the date as tomorrow (J+1)
        with freeze_time(date.today() + timedelta(days=1)):
            # the user comes next day on the website
            self.browser.get(self.live_server_url)
            self.assertTrue(self.wait_page("Maison"))

            # He clicks the "start revision" button
            self.browser.find_element(By.ID, "revision_button_id").click()
            self.assertTrue(self.wait_page("Révision"))

            # He's prompted with a question from a card
            try:
                form = self.browser.find_element(By.ID, "revision_form_id")
            except NoSuchElementException:
                self.fail("Could not find question_text_id")

            success, question_match = self.one_text_in_body(question_pool)
            self.assertTrue(success)
            question_pool.remove(question_match)

            # He answers and clicks on the "check answer" button
            form.find_element(By.ID, "id_answer").send_keys("random")
            self.browser.find_element(By.ID, "check_answer_id").click()

            # He clicks the next button
            self.browser.find_element(By.ID, "next_revision_button_id").click()

            # he's prompted with a question
            try:
                form = self.browser.find_element(By.ID, "revision_form_id")
            except NoSuchElementException:
                self.fail("Could not find question_text_id")

            success, question_match = self.one_text_in_body(question_pool)
            self.assertTrue(success)
            question_pool.remove(question_match)

            # He answers and clicks on the "check answer" button
            form.find_element(By.ID, "id_answer").send_keys("random")
            self.browser.find_element(By.ID, "check_answer_id").click()

            # He clicks the next button
            self.browser.find_element(By.ID, "next_revision_button_id").click()

            # He's prompted with a question he failed yesterday
            try:
                form = self.browser.find_element(By.ID, "revision_form_id")
            except NoSuchElementException:
                self.fail("Could not find question_text_id")

            success, question_match = self.one_text_in_body(question_pool)
            self.assertTrue(success)
            question_pool.remove(question_match)
