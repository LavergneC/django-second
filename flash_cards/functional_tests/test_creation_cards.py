import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as Firefox_Options
from selenium.webdriver.firefox.service import Service


class TestCreationCards(StaticLiveServerTestCase):
    def setUp(self):
        firefox_options = Firefox_Options()

        driverService = Service("/snap/bin/geckodriver")
        self.browser = webdriver.Firefox(service=driverService, options=firefox_options)

    def tearDown(self) -> None:
        self.browser.quit()

    def test_user_create_basic_card(self):
        # the user arrive on the website
        self.browser.get(self.live_server_url)
        self.assertTrue(self.wait_page("Maison"))

        # he clicks the create cards button
        self.browser.find_element(By.ID, "create_button_id").click()
        self.assertTrue(self.wait_page("Nouvelle carte"))

        # The gets a from page
        self.fail("finish the test (tocard)")

        # he fills the from with <quetion><answer>
        # he clicks on the "create" button
        # he's redirected to the home page

    def wait_page(self, page_title: str):
        timeout = 0

        while page_title != self.browser.title:
            time.sleep(0.5)
            timeout += 1

            if timeout > 10:
                return False

        return True
