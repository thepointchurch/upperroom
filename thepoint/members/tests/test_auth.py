from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class TestMembersAuthentication(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "qwerasdf"
        cls.user = get_user_model().objects.create_user(
            username="test", email="test@thepoint.org.au", password=cls.password
        )

    def test_authentication_success(self):
        response = self.client.post(
            settings.LOGIN_URL + "?next=" + reverse("members:index"),
            {"username": self.user.username, "password": self.password},
        )
        self.assertRedirects(response, reverse("members:index"))

    def test_authentication_failure(self):
        response = self.client.post(
            settings.LOGIN_URL,
            {"username": self.user.username, "password": self.password[:-1], "next": reverse("members:index")},
        )
        self.assertEqual(response.status_code, 200)


class TestMembersAuthenticationRequired(TestCase):
    def test_authentication_required_index(self):
        url = reverse("members:index")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_create(self):
        url = reverse("members:create")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_create_confirm(self):
        url = reverse("members:create_confirm", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_tech(self):
        url = reverse("members:tech")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)
