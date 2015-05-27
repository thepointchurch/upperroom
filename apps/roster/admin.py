from django.contrib import admin
from django.forms import ModelForm, ModelMultipleChoiceField

from directory.models import Person
from roster.models import Location, Meeting, Role, RoleType


class RoleInlineForm(ModelForm):
    people = ModelMultipleChoiceField(
        queryset=Person.current_objects.order_by('family__name', 'name'),
        label='People')

    class Meta:
        model = Role
        exclude = ('revision',)


class RoleInline(admin.TabularInline):
    model = Role
    extra = 8
    form = RoleInlineForm

    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class MeetingAdmin(admin.ModelAdmin):
    inlines = [RoleInline]
    list_filter = ('date',)
    search_fields = ['date',
                     'roles__people__name',
                     'roles__people__family__name']

    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Location)
admin.site.register(RoleType)
