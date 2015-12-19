from django.conf import settings
from django.http import Http404

from resources import views
from resources.models import Resource, Tag


class ResourceFallbackMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response
        try:
            slug = request.path_info.strip('/')

            try:
                Tag.featured_objects.get(slug=slug)
                return views.TagList.as_view()(request,
                                               slug=slug).render()
            except AttributeError:
                return response
            except:
                pass

            try:
                Resource.featured_objects.get(slug=slug)
                return views.ResourceDetail.as_view()(request,
                                                      slug=slug).render()
            except:
                pass

            return response

        except Http404:
            return response
        except Exception:
            if settings.DEBUG:
                raise
            return response
