from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from flash_cards.cards.models import Card
from flash_cards.functional_tests.functional_test import FunctionalTest


class TestCardsRevision(FunctionalTest):
    def setUp(self):
        super().setUp()
        Card.objects.create(
            question="Quelle est la capitale de la France ?",
            answer="Paris",
        )
        Card.objects.create(
            question="Quelle est la capitale de l'Italie ?",
            answer="Rome",
        )

    def test_user_do_a_revision(self):
        # the user arrive on the website
        self.browser.get(self.live_server_url)
        self.assertTrue(self.wait_page("Maison"))

        # He clicks the "start revision" button
        self.browser.find_element(By.ID, "revision_button_id").click()
        self.assertTrue(self.wait_page("Révision"))

        # He's prompted with a question from a created card
        try:
            form = self.browser.find_element(By.ID, "revision_form_id")
        except NoSuchElementException:
            self.fail("Could not find question_text_id")

        self.assertTrue(self.text_in_body("Quelle est la capitale de la France ?"))

        # He answer correctly
        form.find_element(By.ID, "id_answer").send_keys("Paris")
        # he clicks on the "check answer" button
        self.browser.find_element(By.ID, "check_answer_id").click()

        # He gets the correct answer and rewarding message
        question = self.browser.find_element(By.ID, "question_text_id").text
        answer = self.browser.find_element(By.ID, "answer_text_id").text

        self.assertEqual(question, "Quelle est la capitale de la France ?")
        self.assertEqual(answer, "Paris")
        self.assertTrue(self.text_in_body("Congratulation !"))

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

        # Since he revised all cards, the next button is not available
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
