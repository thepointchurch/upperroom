import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import include, path, reverse

from ..models import WeblogEntry

urlpatterns = [
    path("members/", include("upperroom.members.urls", namespace="members")),
    path("search/", include("upperroom.search.urls", namespace="search")),
    path("weblog/", include("upperroom.weblog.urls", namespace="weblog")),
]


@override_settings(ROOT_URLCONF=__name__)
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


@override_settings(ROOT_URLCONF=__name__)
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


@override_settings(ROOT_URLCONF=__name__)
class TestResourcesSearchPermissions(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.content = "ead539cf92b4"
        cls.entry = WeblogEntry.objects.create(title="Test", slug="test", description=cls.content, is_published=True)
        cls.content_type = ContentType.objects.get_for_model(WeblogEntry)
        cls.password = "qwerasdf"
        cls.user = get_user_model().objects.create_user(
            username="test", email="test@thepoint.org.au", password=cls.password
        )

    def test_search_public(self):
        url = reverse("search:type", kwargs={"type": self.content_type.id})
        response = self.client.get(url, {"q": "test"})
        self.assertNotContains(response, self.content, status_code=200)

    def test_search_private(self):
        url = reverse("search:type", kwargs={"type": self.content_type.id})
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(url, {"q": "test"})
        self.assertContains(response, self.content, status_code=200)
