import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from ..models import Family


class TestDirectoryAuthentication(TestCase):
    def setUp(self):
        self.password = "qwerasdf"
        self.user = get_user_model().objects.create_user(
            username="test", email="test@thepoint.org.au", password=self.password
        )

    def test_authentication_success(self):
        content_type = ContentType.objects.get_for_model(Family)
        self.user.user_permissions.add(Permission.objects.get(content_type=content_type, codename="can_view"))
        self.user.refresh_from_db()
        response = self.client.post(
            settings.LOGIN_URL + "?next=" + reverse("directory:index"),
            {"username": self.user.username, "password": self.password},
        )
        self.assertRedirects(response, reverse("directory:index"))

    def test_authentication_no_permission(self):
        response = self.client.post(
            settings.LOGIN_URL + "?next=" + reverse("directory:index"),
            {"username": self.user.username, "password": self.password},
        )
        logger = logging.getLogger("django.request")
        previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)
        self.assertRedirects(response, reverse("directory:index"), target_status_code=403)
        logger.setLevel(previous_level)

    def test_authentication_failure(self):
        response = self.client.post(
            settings.LOGIN_URL,
            {"username": self.user.username, "password": self.password[:-1], "next": reverse("directory:index")},
        )
        self.assertEqual(response.status_code, 200)


class TestDirectoryAuthenticationRequired(TestCase):
    def test_authentication_required_index(self):
        url = reverse("directory:index")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_letter(self):
        url = reverse("directory:letter", kwargs={"letter": "a"})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_detail(self):
        url = reverse("directory:detail", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_search(self):
        url = reverse("directory:search")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_edit(self):
        url = reverse("directory:edit")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_birthdays(self):
        url = reverse("directory:birthdays")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_anniversaries(self):
        url = reverse("directory:anniversaries")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_photo(self):
        url = reverse("directory:photo", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_thumbnail(self):
        url = reverse("directory:thumbnail", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_pdf(self):
        url = reverse("directory:pdf")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_print(self):
        url = reverse("directory:print")
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)
