from django import forms
from django.contrib import admin

from directory.models import Family, Person


class PersonInline(admin.TabularInline):
    model = Person
    extra = 1


class FamilyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FamilyForm, self).__init__(*args, **kwargs)
        self.fields['husband'].queryset = \
            Person.objects.filter(family__exact=self.instance.id)\
            .filter(gender__exact='M')
        self.fields['wife'].queryset = \
            Person.objects.filter(family__exact=self.instance.id)\
            .filter(gender__exact='F')


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

admin.site.register(Family, FamilyAdmin)
