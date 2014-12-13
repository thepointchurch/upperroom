from django import forms
from django.contrib import admin

from directory.models import Family, Person


class PersonInline(admin.TabularInline):
    model = Person
    extra = 1

    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


class FamilyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FamilyForm, self).__init__(*args, **kwargs)
        self.fields['husband'].queryset = \
            Person.objects.filter(family__exact=self.instance.id).filter(gender__exact='M')
        self.fields['wife'].queryset = \
            Person.objects.filter(family__exact=self.instance.id).filter(gender__exact='F')


class FamilyAdmin(admin.ModelAdmin):
    inlines = [PersonInline]
    list_filter = ('is_current',)
    search_fields = ['name', 'members__name']
    form = FamilyForm

    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Address', {'fields': ('street', 'suburb', 'postcode')}),
        ('Contact', {'fields': ('email', 'phone_home', 'phone_mobile')}),
        ('Marriage', {'fields': ('anniversary', 'husband', 'wife')}),
        ('Advanced options', {'classes': ('collapse',),
                              'fields': ('is_current',)}),
    )

    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

admin.site.register(Family, FamilyAdmin)
