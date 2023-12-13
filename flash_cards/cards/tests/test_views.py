from django.test import TestCase


class TestNewCardView(TestCase):
    def test_access_new_card_view(self):
        response = self.client.get("/cards/new")
        self.assertEqual(response.status_code, 200)
