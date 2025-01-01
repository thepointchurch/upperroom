# pylint: disable=modelform-uses-exclude

import datetime

from django.contrib import admin
from django.forms import ModelForm, ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _

from ..directory.models import Person
from .models import (
    DAYS_OF_THE_WEEK,
    Location,
    Meeting,
    MeetingTemplate,
    Role,
    RoleType,
    RoleTypeTemplateMapping,
    RosterExclusion,
)


class RoleInlineForm(ModelForm):
    people = ModelMultipleChoiceField(
        required=False, queryset=Person.current_objects.order_by("family__name", "name"), label=_("People")
    )

    class Meta:
        model = Role
        exclude = ("revision",)


class RoleInline(admin.TabularInline):
    model = Role
    form = RoleInlineForm

    def get_extra(self, request, obj=None, **kwargs):
        if obj:
            return 1
        return 8

    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class WeekdayListFilter(admin.SimpleListFilter):
    title = _("weekday")
    parameter_name = "weekday"

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        for week_day_id, week_day in DAYS_OF_THE_WEEK:
            if qs.filter(date__week_day=week_day_id).exists():
                yield (week_day_id, week_day)

    def queryset(self, request, queryset):
        try:
            return queryset.filter(date__week_day=int(self.value()))
        except Exception:  # pylint: disable=broad-except
            return None


class MeetingAdmin(admin.ModelAdmin):
    inlines = [RoleInline]
    date_hierarchy = "date"
    list_filter = (
        "date",
        WeekdayListFilter,
    )
    search_fields = ["date", "roles__people__name", "roles__people__family__name"]

    def get_queryset(self, request):
        return self.model.objects.filter(date__gte=datetime.date.today())

    @admin.action(permissions=["delete"], description=_("Delete past meetings"))
    def delete_past_meetings(self, request, queryset):  # pylint: disable=unused-argument
        queryset.delete(date__lt=datetime.date.today())


class PastMeeting(Meeting):
    class Meta:
        proxy = True


class PastMeetingAdmin(MeetingAdmin):
    def get_queryset(self, request):
        return self.model.objects.filter(date__lt=datetime.date.today())

    def has_add_permission(self, request):  # pylint: disable=unused-argument
        return False

    def has_change_permission(self, request, obj=None):  # pylint: disable=unused-argument
        return False

    def has_delete_permission(self, request, obj=None):  # pylint: disable=unused-argument
        return False


class RoleTypeAdmin(admin.ModelAdmin):
    actions = ["empty_role_type_servers"]

    @admin.action(description=_("Empty servers from role types"))
    def empty_role_type_servers(self, request, queryset):  # pylint: disable=unused-argument
        for role_type in queryset.all():
            role_type.servers.clear()


class RoleTypeMappingInline(admin.TabularInline):
    model = RoleTypeTemplateMapping
    extra = 1
    verbose_name = "role type"
    verbose_name_plural = "role types"


class MeetingTemplateAdmin(admin.ModelAdmin):
    inlines = [RoleTypeMappingInline]


class ExclusionDateInline(admin.TabularInline):
    model = RosterExclusion
    extra = 1


class ExclusionAdmin(admin.ModelAdmin):
    inlines = [ExclusionDateInline]
    fields = [()]
    actions = ["delete_past_exclusions"]

    def get_queryset(self, request):
        return self.model.objects.filter(is_current=True).exclude(role_types=None)

    @admin.action(
        permissions=["delete"], description=_("Delete past " + str(RosterExclusion._meta.verbose_name_plural))
    )
    def delete_past_exclusions(self, request, queryset):
        for person in queryset.all():
            person.exclusions.filter(date__lt=datetime.date.today()).delete()

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions["delete_selected"]
        return actions


class ExclusionPerson(Person):
    class Meta:
        proxy = True

        verbose_name = _("server exclusion date")
        verbose_name_plural = _("exclusion dates")


admin.site.register(Meeting, MeetingAdmin)
admin.site.register(PastMeeting, PastMeetingAdmin)
admin.site.register(Location)
admin.site.register(ExclusionPerson, ExclusionAdmin)
admin.site.register(RoleType, RoleTypeAdmin)
admin.site.register(MeetingTemplate, MeetingTemplateAdmin)
