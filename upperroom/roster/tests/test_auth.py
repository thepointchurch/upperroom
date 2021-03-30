from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import include, path, reverse

from ...directory.models import Family

urlpatterns = [
    path("members/", include("upperroom.members.urls", namespace="members")),
    path("roster/", include("upperroom.roster.urls", namespace="roster")),
]


@override_settings(ROOT_URLCONF=__name__)
class TestRosterAuthentication(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "qwerasdf"
        cls.user = get_user_model().objects.create_user(
            username="test", email="test@thepoint.org.au", password=cls.password
        )

    def test_authentication_success(self):
        response = self.client.post(
            settings.LOGIN_URL + "?next=" + reverse("roster:index"),
            {"username": self.user.username, "password": self.password},
        )
        self.assertRedirects(response, reverse("roster:index"))

    def test_authentication_failure(self):
        response = self.client.post(
            settings.LOGIN_URL,
            {"username": self.user.username, "password": self.password[:-1], "next": reverse("roster:index")},
        )
        self.assertEqual(response.status_code, 200)


@override_settings(ROOT_URLCONF=__name__)
class TestRosterAuthenticationRequired(TestCase):
    def test_authentication_required_index(self):
        url = reverse("roster:index")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_meeting_month(self):
        url = reverse("roster:meeting_month", kwargs={"year": 2020, "month": 1})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_pdf(self):
        url = reverse("roster:pdf", kwargs={"year": 2020})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_person(self):
        url = reverse("roster:person", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_builder(self):
        url = reverse("roster:builder")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)


@override_settings(ROOT_URLCONF=__name__)
class TestRosterAuthenticationNotRequired(TestCase):
    @classmethod
    def setUpTestData(cls):
        family = Family.objects.create(name="Doe")
        cls.person = family.members.create(name="John", email="test@thepoint.org.au")

    def test_authentication_not_required_event(self):
        response = self.client.get(reverse("roster:event", kwargs={"pk": self.person.id}))
        self.assertEqual(response.status_code, 200)

    def test_authentication_not_required_task(self):
        response = self.client.get(reverse("roster:task", kwargs={"pk": self.person.id}))
        self.assertEqual(response.status_code, 200)
