# pylint: disable=too-many-ancestors

from pathlib import Path

from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from django.views import generic

from ..utils.mixin import NeverCacheMixin


class SearchView(NeverCacheMixin, generic.TemplateView):
    template_name = "search/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content_type_id = kwargs.get("type")
        page = self.request.GET.get("page")
        context["search_query"] = self.request.GET.get("q", "")
        context["search_results"] = {}
        context["type_name"] = None
        for content_type in ContentType.objects.all():
            cls = content_type.model_class()
            if content_type_id is not None and int(content_type_id) != content_type.id:
                continue
            try:
                paginator = Paginator(
                    cls.search_objects.search(context["search_query"]).filter(
                        cls.search_objects.get_custom_filter(self.request)
                    ),
                    5,
                ).page(page or 1)
                if paginator.object_list:
                    context["search_results"][cls._meta.verbose_name_plural] = {
                        "page": paginator,
                        "template": Path(cls._meta.app_config.path).name + "/search_result.html",
                        "type": content_type.id,
                    }
                if content_type_id is not None:
                    context["type_name"] = cls._meta.verbose_name_plural
            except AttributeError:
                continue
        return context
