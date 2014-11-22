from django import forms
from directory.models import Person, Family
from django.contrib import admin

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
        self.fields['husband'].queryset = Person.objects.filter(family__exact=self.instance.id).filter(gender__exact='M')
        self.fields['wife'].queryset = Person.objects.filter(family__exact=self.instance.id).filter(gender__exact='F')

class FamilyAdmin(admin.ModelAdmin):
    inlines = [PersonInline]
    list_filter = ('is_current',)
    search_fields = ['name', 'members__name']
    form = FamilyForm

    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

admin.site.register(Family, FamilyAdmin)
