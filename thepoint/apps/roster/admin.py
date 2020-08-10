from django.contrib import admin
from django.forms import ModelForm, ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _

from .models import Location, Meeting, MeetingTemplate, Role, RoleType, RoleTypeTemplateMapping, DAYS_OF_THE_WEEK
from ..directory.models import Person


class RoleInlineForm(ModelForm):
    people = ModelMultipleChoiceField(
        required=False,
        queryset=Person.current_objects.order_by('family__name', 'name'),
        label=_('People'))

    class Meta:
        model = Role
        exclude = ('revision',)


class RoleInline(admin.TabularInline):
    model = Role
    form = RoleInlineForm

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 1
        else:
            return 8

    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class WeekdayListFilter(admin.SimpleListFilter):
    title = _('weekday')
    parameter_name = 'weekday'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        for week_day_id, week_day in DAYS_OF_THE_WEEK:
            if qs.filter(date__week_day=week_day_id).exists():
                yield (week_day_id, week_day)

    def queryset(self, request, queryset):
        try:
            return queryset.filter(date__week_day=int(self.value()))
        except:
            pass


class MeetingAdmin(admin.ModelAdmin):
    inlines = [RoleInline]
    list_filter = ('date', WeekdayListFilter,)
    search_fields = ['date',
                     'roles__people__name',
                     'roles__people__family__name']

    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class RoleTypeMappingInline(admin.TabularInline):
    model = RoleTypeTemplateMapping
    extra = 1
    verbose_name = 'role type'
    verbose_name_plural = 'role types'


class MeetingTemplateAdmin(admin.ModelAdmin):
    inlines = [RoleTypeMappingInline]


admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Location)
admin.site.register(RoleType)
admin.site.register(MeetingTemplate, MeetingTemplateAdmin)
