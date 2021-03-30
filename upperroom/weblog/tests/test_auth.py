import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class TestWeblogAuthentication(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "qwerasdf"
        cls.user = get_user_model().objects.create_user(
            username="test", email="test@thepoint.org.au", password=cls.password
        )

    def test_authentication_success(self):
        response = self.client.post(
            settings.LOGIN_URL + "?next=" + reverse("weblog:index"),
            {"username": self.user.username, "password": self.password},
        )
        self.assertRedirects(response, reverse("weblog:index"))

    def test_authentication_failure(self):
        response = self.client.post(
            settings.LOGIN_URL,
            {"username": self.user.username, "password": self.password[:-1], "next": reverse("weblog:index")},
        )
        self.assertEqual(response.status_code, 200)


class TestWeblogAuthenticationRequired(TestCase):
    def test_authentication_required_index(self):
        url = reverse("weblog:index")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_detail(self):
        url = reverse("weblog:detail", kwargs={"slug": "test", "year": 2020, "month": 1})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_attachment(self):
        url = reverse("weblog:attachment", kwargs={"pk": uuid.uuid4()})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)
