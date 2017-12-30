from django.contrib import admin

from .models import Issue, Publication


class IssueAdmin(admin.ModelAdmin):
    model = Issue,
    list_filter = ('date', 'publication',)
    search_fields = ['date']


admin.site.register(Publication)
admin.site.register(Issue, IssueAdmin)
