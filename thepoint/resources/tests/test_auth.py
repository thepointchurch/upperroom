from unittest.mock import MagicMock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.test import TestCase
from django.urls import reverse

from ..models import Resource, Tag


class TestResourcesAuthentication(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = "qwerasdf"
        cls.user = get_user_model().objects.create_user(
            username="test", email="test@thepoint.org.au", password=cls.password
        )

    def test_authentication_success(self):
        response = self.client.post(
            settings.LOGIN_URL + "?next=" + reverse("resources:index"),
            {"username": self.user.username, "password": self.password},
        )
        self.assertRedirects(response, reverse("resources:index"))

    def test_authentication_failure(self):
        response = self.client.post(
            settings.LOGIN_URL,
            {"username": self.user.username, "password": self.password[:-1], "next": reverse("resources:index")},
        )
        self.assertEqual(response.status_code, 200)


class TestResourcesAuthenticationRequired(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.resource = Resource.objects.create(
            title="Test", slug="test", body="test", is_published=True, is_private=True
        )
        cls.mock_file = MagicMock(spec=File)
        cls.mock_file.name = "test.txt"
        cls.tag = Tag.objects.create(name="Test", slug="test", is_private=True)
        cls.tagged_resource = cls.tag.resources.create(
            title="Test", slug="tagged", body="test", is_published=True, is_private=False
        )

    def test_authentication_required_attachment(self):
        attachment = self.resource.attachments.create(title="Test", slug="test", file=self.mock_file)
        url = reverse("resources:attachment", kwargs={"pk": attachment.id})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_attachment_tagged(self):
        tagged_attachment = self.tagged_resource.attachments.create(title="Test", slug="test", file=self.mock_file)
        url = reverse("resources:attachment", kwargs={"pk": tagged_attachment.id})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_detail(self):
        url = reverse("resources:detail", kwargs={"slug": self.resource.slug})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_detail_tagged(self):
        url = reverse("resources:detail", kwargs={"slug": self.tagged_resource.slug})
        response = self.client.get(url)
        self.assertRedirects(response, settings.LOGIN_URL + "?next=" + url)

    def test_authentication_required_tag(self):
        response = self.client.get(reverse("resources:tag", kwargs={"slug": self.tag.slug}))
        self.assertEqual(response.status_code, 404)


class TestResourcesAuthenticationNotRequired(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.resource = Resource.objects.create(
            title="Test", slug="test", body="test", is_published=True, is_private=False
        )
        cls.mock_file = MagicMock(spec=File)
        cls.mock_file.name = "test.txt"
        cls.tag = Tag.objects.create(name="Test", slug="test", is_private=False)
        cls.tagged_resource = cls.tag.resources.create(
            title="Test", slug="tagged", body="test", is_published=True, is_private=False
        )

    def test_authentication_not_required_attachment(self):
        attachment = self.resource.attachments.create(title="Test", slug="test", file=self.mock_file)
        url = reverse("resources:attachment", kwargs={"pk": attachment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_authentication_not_required_attachment_tagged(self):
        tagged_attachment = self.tagged_resource.attachments.create(title="Test", slug="test", file=self.mock_file)
        url = reverse("resources:attachment", kwargs={"pk": tagged_attachment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_authentication_not_required_detail(self):
        url = reverse("resources:detail", kwargs={"slug": self.resource.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_authentication_not_required_detail_tagged(self):
        url = reverse("resources:detail", kwargs={"slug": self.tagged_resource.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_authentication_not_required_tag(self):
        url = reverse("resources:tag", kwargs={"slug": self.tag.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
