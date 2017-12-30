from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Family, Person
from .signals import family_updated


class PersonInline(admin.TabularInline):
    model = Person
    extra = 1

    def formfield_for_dbfield(self, db_field, **kwargs):
        field = super(PersonInline, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'suffix':
            field.widget.attrs['style'] = 'width: 5em;'
        return field


class FamilyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FamilyForm, self).__init__(*args, **kwargs)
        self.fields['husband'].queryset = (
            Person.objects
            .filter(family__exact=self.instance.id)
            .filter(gender__exact='M')
            )
        self.fields['wife'].queryset = (
            Person.objects
            .filter(family__exact=self.instance.id)
            .filter(gender__exact='F')
            )


def action_mark_current(modeladmin, request, queryset):
    for f in queryset.all():
        f.is_current = True
        f.save()


action_mark_current.short_description = _('Mark selected families as current')


def action_unmark_current(modeladmin, request, queryset):
    for f in queryset.all():
        f.is_current = False
        f.save()


action_unmark_current.short_description = _('Mark selected families as not current')


class FamilyAdmin(admin.ModelAdmin):
    inlines = [PersonInline]
    list_filter = ('is_current',)
    search_fields = ['name', 'members__name']
    form = FamilyForm
    actions = [action_mark_current, action_unmark_current]

    fieldsets = (
        (None, {'fields': ('name',)}),
        (_('Address'), {'fields': ('street', 'suburb', 'postcode')}),
        (_('Contact'), {'fields': ('email', 'phone_home', 'phone_mobile')}),
        (_('Marriage'), {'fields': ('anniversary', 'husband', 'wife')}),
        (_('Advanced options'), {'classes': ('collapse',),
                                 'fields': ('is_current',)}),
    )

    def save_related(self, request, form, formsets, change):
        super(FamilyAdmin, self).save_related(request, form, formsets, change)
        family_updated.send(sender=form.instance.__class__, instance=form.instance)


class PersonAdmin(admin.ModelAdmin):
    list_filter = ('is_current',)
    search_fields = ['name', 'family__name']
    ordering = ('name', 'family__name')


admin.site.register(Family, FamilyAdmin)
admin.site.register(Person, PersonAdmin)
