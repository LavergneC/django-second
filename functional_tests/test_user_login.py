from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from flash_cards.cards.models import Card
from flash_cards.users.tests.factories import UserFactory
from functional_tests.functional_test import FunctionalTest


class TestUserLogin(FunctionalTest):
    def setUp(self):
        super().setUp()

        self.user = UserFactory(
            password="plopplop",
        )

        Card.objects.create(
            question="Quel est la capital de la Lettonie",
            answer="Riga",
            user=self.user,
        )

    def test_user_arrives_and_login(self):
        # the user arrive on the website
        self.browser.get(self.live_server_url)
        self.assertTrue(self.wait_page("Maison"))

        # Since he's not conencted yet, he can't create a new card
        try:
            self.browser.find_element(By.ID, "create_page_button_id").click()
            self.fail("Should NOT find create button before login")
        except NoSuchElementException:
            pass

        # Since he's not conencted yet, he can't revise
        try:
            self.browser.find_element(By.ID, "revision_button_id").click()
            self.fail("Should NOT find revision button before login")
        except NoSuchElementException:
            pass

        # he clicks the Sign In button
        self.browser.find_element(By.ID, "log-in-link").click()
        # he gets the Sign In page, enter is credentials and clicks "Sign In"
        self.assertTrue(self.wait_page("Sign In"))
        self.browser.find_element(By.ID, "id_login").send_keys(self.user.email)
        self.browser.find_element(By.ID, "id_password").send_keys("plopplop")
        self.browser.find_element(By.CLASS_NAME, "primaryAction").click()

        # he's redirected to the main page
        self.assertTrue(self.wait_page("Maison"))

        # The buttons are now in tha pages
        try:
            self.browser.find_element(By.ID, "create_page_button_id")
            self.browser.find_element(By.ID, "revision_button_id")
        except NoSuchElementException:
            self.fail("create_page_button_id or revision_button_id not present in the page after login")
