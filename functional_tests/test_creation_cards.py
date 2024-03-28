from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from flash_cards.users.tests.factories import UserFactory
from functional_tests.functional_test import FunctionalTest


class TestCreationCards(FunctionalTest):
    def setUp(self):
        super().setUp()
        UserFactory(
            email="clement@example.fr",
            password="plopplop",
        )

    def test_user_login_and_create_basic_card(self):
        # the user arrive on the website
        self.browser.get(self.live_server_url)
        self.assertTrue(self.wait_page("Maison"))

        # Since he's not conencted yet, he can't create a new card
        try:
            self.browser.find_element(By.ID, "create_page_button_id").click()
            self.fail("Should NOT find create button before login")
        except NoSuchElementException:
            pass

        # he clicks the Sign In button
        self.browser.find_element(By.ID, "log-in-link").click()
        # he gets the Sign In page, enter is credentials and clicks "Sign In"
        self.assertTrue(self.wait_page("Sign In"))
        self.browser.find_element(By.ID, "id_login").send_keys("clement@example.fr")
        self.browser.find_element(By.ID, "id_password").send_keys("plopplop")
        self.browser.find_element(By.CLASS_NAME, "primaryAction").click()

        # he's redirected to the main page
        self.assertTrue(self.wait_page("Maison"))

        # he clicks the create cards button
        self.browser.find_element(By.ID, "create_page_button_id").click()
        self.assertTrue(self.wait_page("Nouvelle carte"))

        # he gets a form the a card creation
        form = self.browser.find_element(By.ID, "create_card_form_id")
        self.assertIsNotNone(form)

        # he fills the form with <question><answer>
        form.find_element(By.ID, "question_field_id").send_keys("Quelle est la capitale de la France ?")
        form.find_element(By.ID, "answer_field_id").send_keys("Paris")

        # he clicks on the "create" button
        self.browser.find_element(By.ID, "create_button_id").click()

        # he's redirected to the home page where a message says it worked
        self.assertTrue(self.wait_page("Maison"))
        self.assertTrue(self.text_in_body("Card succesfully created."))

    def test_user_fail_to_create_basic_card(self):
        # the user arrive on the website
        self.browser.get(self.live_server_url)
        self.assertTrue(self.wait_page("Maison"))

        # he clicks the create cards button
        self.browser.find_element(By.ID, "create_page_button_id").click()
        self.assertTrue(self.wait_page("Nouvelle carte"))

        # he gets a form the a card creation
        form = self.browser.find_element(By.ID, "create_card_form_id")
        self.assertIsNotNone(form)

        # he fills the form with <question> but an empty answer
        form.find_element(By.ID, "question_field_id").send_keys("Quelle est la capitale de la France ?")

        # he clicks on the "create" button
        self.browser.find_element(By.ID, "create_button_id").click()

        # he stays on the page and get an error message
        self.assertTrue(self.wait_page("Nouvelle carte"))
