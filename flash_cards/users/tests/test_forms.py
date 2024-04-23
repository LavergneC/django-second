"""
Module for all Form Tests.
"""

from unittest.mock import patch

from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.translation import gettext_lazy as _

from flash_cards.users.forms import UserAdminCreationForm, UserSignupForm
from flash_cards.users.models import User


class TestUserAdminCreationForm:
    """
    Test class for all tests related to the UserAdminCreationForm
    """

    def test_username_validation_error_msg(self, user: User):
        """
        Tests UserAdminCreation Form's unique validator functions correctly by testing:
            1) A new user with an existing username cannot be added.
            2) Only 1 error is raised by the UserCreation Form
            3) The desired error message is raised
        """

        # The user already exists,
        # hence cannot be created.
        form = UserAdminCreationForm(
            {
                "email": user.email,
                "password1": user.password,
                "password2": user.password,
            }
        )

        assert not form.is_valid()
        assert len(form.errors) == 1
        assert "email" in form.errors
        assert form.errors["email"][0] == _("This email has already been taken.")


class TestCreateAccountForm(TestCase):
    def test_display_fields(self):
        form = UserSignupForm()
        self.assertIn('id="id_email"', form.as_p())
        self.assertIn('id="id_name"', form.as_p())
        self.assertIn('id="id_password1"', form.as_p())
        self.assertIn('id="id_password2"', form.as_p())

    @patch("allauth.account.adapter.DefaultAccountAdapter.unstash_verified_email")
    def test_save_email_and_name(self, mock_unstash_verified_email):
        fake_request = RequestFactory()

        email = "dupont@example.fr"
        form = UserSignupForm(
            data={
                "email": email,
                "name": "jean dupont",
                "password1": "passPass",
                "password2": "passPass",
            }
        )
        form.full_clean()

        mock_unstash_verified_email.return_value = email
        user = form.save(fake_request)
        self.assertEqual(user.email, email)
        self.assertEqual(user.name, "jean dupont")
