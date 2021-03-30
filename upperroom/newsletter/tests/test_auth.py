import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import include, path, reverse

from ..models import Publication

urlpatterns = [
    path("members/", include("upperroom.members.urls", namespace="members")),
    path("news/", include("upperroom.newsletter.urls", namespace="news")),
]


@override_settings(ROOT_URLCONF=__name__)
class TestNewsletterAuthentication(TestCase):
    @classmethod
    def setUpTestData(cls):
        Publication.objects.create(slug="news", name="News", is_private=True)
        cls.password = "qwerasdf"
        cls.user = get_user_model().objects.create_user(
            username="test", email="test@thepoint.org.au", password=cls.password
        )

    def test_authentication_success(self):
        response = self.client.post(
            settings.LOGIN_URL + "?next=" + reverse("news:index"),
            {"username": self.user.username, "password": self.password},
        )
        self.assertRedirects(response, reverse("news:index"))

    def test_authentication_failure(self):
        response = self.client.post(
            settings.LOGIN_URL,
            {"username": self.user.username, "password": self.password[:-1], "next": reverse("news:index")},
        )
        self.assertEqual(response.status_code, 200)


@override_settings(ROOT_URLCONF=__name__)
class TestNewsletterAuthenticationRequired(TestCase):
    @classmethod
    def setUpTestData(cls):
        Publication.objects.create(slug="news", name="News", is_private=True)

    def test_authentication_required_index(self):
        url = reverse("news:index")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_issue(self):
        url = reverse("newsletter:issue", kwargs={"slug": datetime.date.today().isoformat()})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)
