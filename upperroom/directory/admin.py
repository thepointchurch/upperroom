from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Family, Person
from .signals import family_updated


class PersonInline(admin.TabularInline):
    model = Person
    extra = 1

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        field = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "suffix":
            field.widget.attrs["style"] = "width: 5em;"
        return field


class FamilyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["husband"].queryset = Person.objects.filter(family__exact=self.instance.id).filter(
            gender__exact="M"
        )
        self.fields["wife"].queryset = Person.objects.filter(family__exact=self.instance.id).filter(gender__exact="F")


class ArchivedFamilyListFilter(admin.SimpleListFilter):
    title = _("archived")
    parameter_name = "archived"

    def lookups(self, request, model_admin):
        return (("yes", _("Yes")), ("no", _("No")))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(is_archived=True)
        if self.value() == "no":
            return queryset.filter(is_archived=False)
        return None


class FamilyAdmin(admin.ModelAdmin):
    inlines = [PersonInline]
    list_filter = ("is_current", ArchivedFamilyListFilter)
    search_fields = ["name", "members__name"]
    form = FamilyForm
    actions = ["mark_current", "nmark_current", "mark_archived", "mark_unarchived"]

    fieldsets = (
        (None, {"fields": ("name",)}),
        (_("Address"), {"fields": ("street", "suburb", "postcode")}),
        (_("Contact"), {"fields": ("email", "phone_home", "phone_mobile")}),
        (_("Marriage"), {"fields": ("anniversary", "husband", "wife")}),
        (_("Photo"), {"fields": ("photo",)}),
        (_("Advanced options"), {"classes": ("collapse",), "fields": ("is_current", "is_archived")}),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        family_updated.send(sender=form.instance.__class__, instance=form.instance, actor=request.user)

    @admin.action(description=_("Mark selected families as current"))
    def mark_current(self, request, queryset):  # pylint: disable=unused-argument
        for family in queryset.all():
            family.is_current = True
            family.save()

    @admin.action(description=_("Mark selected families as not current"))
    def unmark_current(self, request, queryset):  # pylint: disable=unused-argument
        for family in queryset.all():
            family.is_current = False
            family.save()

    @admin.action(description=_("Archive selected families"))
    def mark_archived(self, request, queryset):  # pylint: disable=unused-argument
        for family in queryset.all():
            family.is_archived = True
            family.save()

    @admin.action(description=_("Unrchive selected families"))
    def mark_unarchived(self, request, queryset):  # pylint: disable=unused-argument
        for family in queryset.all():
            family.is_archived = False
            family.save()


class PersonAdmin(admin.ModelAdmin):
    list_filter = ("is_current",)
    search_fields = ["name", "family__name"]
    ordering = ("name", "family__name")


admin.site.register(Family, FamilyAdmin)
admin.site.register(Person, PersonAdmin)
