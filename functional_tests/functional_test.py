import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as Firefox_Options
from selenium.webdriver.firefox.service import Service

from flash_cards.users.tests.factories import UserFactory


class FunctionalTest(StaticLiveServerTestCase):
    def setUp(self):
        firefox_options = Firefox_Options()

        driverService = Service("/snap/bin/geckodriver")
        self.browser = webdriver.Firefox(service=driverService, options=firefox_options)

    def tearDown(self) -> None:
        self.browser.quit()

    def text_in_body(self, text: str) -> bool:
        body = self.browser.find_element(By.TAG_NAME, "body").text
        return text in body

    def wait_page(self, page_title: str):
        timeout = 0

        while page_title != self.browser.title:
            time.sleep(0.5)
            timeout += 1

            if timeout > 10:
                return False

        return True

    def login(self):
        self.client = Client()
        self.user = UserFactory(password="salut")
        self.client.login(email=self.user.email, password="salut")
        self.cookie = self.client.cookies["sessionid"]
        self.browser.get(self.live_server_url + "/fake-path")
        self.browser.add_cookie(
            {
                "name": "sessionid",
                "value": self.cookie.value,
                "path": "/",
            }
        )
