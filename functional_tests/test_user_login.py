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

        # Since he's not conencted yet, he can't create a new card, revise or see it's cards
        self.check_element_absence("create_page_button_id")
        self.check_element_absence("revision_button_id")
        self.check_element_absence("card_list_button_id")

        # he clicks the Sign In button
        self.browser.find_element(By.ID, "log-in-link").click()
        # he gets the Sign In page, enter is credentials and clicks "Sign In"
        self.assertTrue(self.wait_page("Sign In"))
        self.browser.find_element(By.ID, "id_login").send_keys(self.user.email)
        self.browser.find_element(By.ID, "id_password").send_keys("plopplop")
        self.browser.find_element(By.CLASS_NAME, "primaryAction").click()

        # he's redirected to the main page
        self.assertTrue(self.wait_page("Maison"))

        # The buttons are now in the page
        self.check_element_presence("create_page_button_id")
        self.check_element_presence("revision_button_id")
        self.check_element_presence("card_list_button_id")

    def test_user_create_an_account(self):
        # the user arrive on the website
        self.browser.get(self.live_server_url)
        self.assertTrue(self.wait_page("Maison"))

        # Since he's not conencted yet, he can't create a new card, revise or see it's cards
        self.check_element_absence("create_page_button_id")
        self.check_element_absence("revision_button_id")
        self.check_element_absence("card_list_button_id")

        # he clicks the Sign Up button
        self.browser.find_element(By.ID, "sign-up-link").click()
        self.assertTrue(self.wait_page("Signup"))

        # he gets the Sign Up page, enter is credentials
        new_user_login = "JeanDupont@wanadoo.fr"
        new_user_name = "Jean Jean la mémoire"
        new_user_password = "53cur3#P455w0r6"

        self.browser.find_element(By.ID, "id_email").send_keys(new_user_login)
        self.browser.find_element(By.ID, "id_name").send_keys(new_user_name)
        self.browser.find_element(By.ID, "id_password1").send_keys(new_user_password)
        self.browser.find_element(By.ID, "id_password2").send_keys(new_user_password)

        # He clicks "Sign Up >>"
        self.browser.find_element(By.CLASS_NAME, "btn-primary").click()

        # he's redirected to the main page
        self.assertTrue(self.wait_page("Maison"))

        # The buttons are now in the page
        self.check_element_presence("create_page_button_id")
        self.check_element_presence("revision_button_id")
        self.check_element_presence("card_list_button_id")

        # He then checks his informations by clicking "My Profile"
        self.browser.find_element(By.XPATH, '//a[@class="nav-link" and contains(@href, "/users/")]').click()

        # his name apears in both the page title and content
        self.assertTrue(self.wait_page("User: " + new_user_name))
        self.assertTrue(self.text_in_body(new_user_name))
