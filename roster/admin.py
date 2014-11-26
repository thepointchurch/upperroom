from django.contrib import admin

from roster.models import Location, Meeting, Role, RoleType

class RoleInline(admin.TabularInline):
    model = Role
    extra = 8
    exclude = ('revision',)

    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

class MeetingAdmin(admin.ModelAdmin):
    inlines = [RoleInline]
    list_filter = ('date',)
    search_fields = ['date', 'roles__person__name', 'roles__person__family__name']

    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Location)
admin.site.register(RoleType)
