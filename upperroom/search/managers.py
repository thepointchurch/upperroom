from django.db import models


class SearchManager(models.Manager):
    def __init__(self, **kwargs):
        super().__init__()
        self.search_fields = kwargs

    def get_custom_filter(self, request=None):
        return models.Q()

    def search(self, query):
        queryset = self.get_queryset()
        combined_filter = None
        for term, operator in self.search_fields.items():
            query_filter = models.Q(**{f"{term}__{operator}": query})
            if combined_filter:
                combined_filter = combined_filter | query_filter
            else:
                combined_filter = query_filter
        if combined_filter:
            queryset = queryset.filter(combined_filter)
        return queryset
