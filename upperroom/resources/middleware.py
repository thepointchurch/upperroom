from django.conf import settings
from django.http import Http404

from . import views
from .models import Resource, Tag


class ResourceFallbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response = self.process_response(request, response)
        return response

    def process_response(self, request, response):  # NOQA: C901 pylint: disable=too-many-return-statements
        if response.status_code != 404:
            return response
        try:
            slug = request.path_info.strip("/")

            if Tag.featured_objects.filter(slug=slug).only("slug"):
                return views.TagList.as_view()(request, slug=slug).render()
            if Resource.featured_objects.filter(slug=slug).only("slug"):
                return views.ResourceDetail.as_view()(request, slug=slug).render()
            return response

        except Http404:
            return response
        except Exception:  # pylint: disable=broad-except
            if settings.DEBUG:
                raise
            return response
