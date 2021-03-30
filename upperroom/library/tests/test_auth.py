from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import include, path, reverse

urlpatterns = [
    path("members/", include("upperroom.members.urls", namespace="members")),
    path("library/", include("upperroom.library.urls", namespace="library")),
]


@override_settings(ROOT_URLCONF=__name__)
class TestLibraryAuthentication(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "qwerasdf"
        cls.user = get_user_model().objects.create_user(
            username="test", email="test@thepoint.org.au", password=cls.password
        )

    def test_authentication_success(self):
        response = self.client.post(
            settings.LOGIN_URL + "?next=" + reverse("library:index"),
            {"username": self.user.username, "password": self.password},
        )
        self.assertRedirects(response, reverse("library:index"))

    def test_authentication_failure(self):
        response = self.client.post(
            settings.LOGIN_URL,
            {"username": self.user.username, "password": self.password[:-1], "next": reverse("library:index")},
        )
        self.assertEqual(response.status_code, 200)


@override_settings(ROOT_URLCONF=__name__)
class TestLibraryAuthenticationRequired(TestCase):
    def test_authentication_required_index(self):
        url = reverse("library:index")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_search(self):
        url = reverse("library:search")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)
