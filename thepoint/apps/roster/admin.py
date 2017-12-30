from django.contrib import admin
from django.forms import ModelForm, ModelMultipleChoiceField
from django.utils.translation import ugettext_lazy as _

from .models import Location, Meeting, Role, RoleType
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
    extra = 8
    form = RoleInlineForm

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
        if qs.filter(date__week_day=1).exists():
            yield ('1', _('Sunday'))
        if qs.filter(date__week_day=2).exists():
            yield ('2', _('Monday'))
        if qs.filter(date__week_day=3).exists():
            yield ('3', _('Tuesday'))
        if qs.filter(date__week_day=4).exists():
            yield ('4', _('Wednesday'))
        if qs.filter(date__week_day=5).exists():
            yield ('5', _('Thursday'))
        if qs.filter(date__week_day=6).exists():
            yield ('6', _('Friday'))
        if qs.filter(date__week_day=7).exists():
            yield ('7', _('Saturday'))

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


admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Location)
admin.site.register(RoleType)
