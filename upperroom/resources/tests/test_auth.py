from unittest.mock import MagicMock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.storage import default_storage
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import include, path, reverse

from ..models import Resource, Tag

urlpatterns = [
    path("members/", include("upperroom.members.urls", namespace="members")),
    path("resources/", include("upperroom.resources.urls", namespace="resources")),
    path("search/", include("upperroom.search.urls", namespace="search")),
]


@override_settings(ROOT_URLCONF=__name__)
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


@override_settings(ROOT_URLCONF=__name__)
class TestResourcesAuthenticationRequired(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.resource = Resource.objects.create(
            title="Test", slug="test", body="test", is_published=True, is_private=True
        )
        cls.mock_file = MagicMock(spec=File)
        cls.mock_file.name = "test.txt"
        cls.tag = Tag.objects.create(name="Test", slug="test", is_private=True)
        cls.tag_content = "c7b92ef2fb60"
        cls.tagged_resource = cls.tag.resources.create(
            title="Test", slug="tagged", description=cls.tag_content, body="test", is_published=True, is_private=False
        )
        cls.password = "qwerasdf"
        cls.user = get_user_model().objects.create_user(
            username="test", email="test@thepoint.org.au", password=cls.password
        )

    def test_authentication_required_attachment(self):
        attachment = self.resource.attachments.create(title="Test", slug="test", file=self.mock_file)
        url = reverse("resources:attachment", kwargs={"pk": attachment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        default_storage.delete(attachment.file.name)

    def test_authentication_required_attachment_tagged(self):
        tagged_attachment = self.tagged_resource.attachments.create(title="Test", slug="test", file=self.mock_file)
        url = reverse("resources:attachment", kwargs={"pk": tagged_attachment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        default_storage.delete(tagged_attachment.file.name)

    def test_authentication_required_detail(self):
        url = reverse("resources:detail", kwargs={"slug": self.resource.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_authentication_required_detail_tagged(self):
        url = reverse("resources:detail", kwargs={"slug": self.tagged_resource.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_authentication_required_tag(self):
        response = self.client.get(reverse("resources:tag", kwargs={"slug": self.tag.slug}))
        self.assertEqual(response.status_code, 404)

    def test_authentication_required_tag_list(self):
        url = reverse("resources:index")
        response = self.client.get(url)
        self.assertNotContains(response, self.tag_content, status_code=200)
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(url)
        self.assertContains(response, self.tag_content, status_code=200)


@override_settings(ROOT_URLCONF=__name__)
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
        attachment = self.resource.attachments.create(
            title="Test", slug="test", mime_type="text/plain", file=self.mock_file
        )
        url = reverse("resources:attachment", kwargs={"pk": attachment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        default_storage.delete(attachment.file.name)

    def test_authentication_not_required_attachment_tagged(self):
        tagged_attachment = self.tagged_resource.attachments.create(
            title="Test", slug="test", mime_type="text/plain", file=self.mock_file
        )
        url = reverse("resources:attachment", kwargs={"pk": tagged_attachment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        default_storage.delete(tagged_attachment.file.name)

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


@override_settings(ROOT_URLCONF=__name__)
class TestResourcesSearchPermissions(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.public_content = "10e4c8c9a1df"
        cls.public_resource = Resource.objects.create(
            title="Public Test", slug="public", description=cls.public_content, is_published=True, is_private=False
        )
        cls.private_content = "46f7e7f0de85"
        cls.private_resource = Resource.objects.create(
            title="Private Test", slug="private", description=cls.private_content, is_published=True, is_private=True
        )
        cls.content_type = ContentType.objects.get_for_model(Resource)
        cls.password = "qwerasdf"
        cls.user = get_user_model().objects.create_user(
            username="test", email="test@thepoint.org.au", password=cls.password
        )

    def test_search_public(self):
        url = reverse("search:type", kwargs={"type": self.content_type.id})
        response = self.client.get(url, {"q": "test"})
        self.assertContains(response, self.public_content, status_code=200)
        self.assertNotContains(response, self.private_content, status_code=200)

    def test_search_private(self):
        url = reverse("search:type", kwargs={"type": self.content_type.id})
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(url, {"q": "test"})
        self.assertContains(response, self.public_content, status_code=200)
        self.assertContains(response, self.private_content, status_code=200)
