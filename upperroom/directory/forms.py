from django.forms import DateInput, ModelForm
from django.forms.models import inlineformset_factory, modelform_factory

from .admin import FamilyForm as AdminFamilyForm
from .models import Family, Person


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = [
            "name",
            "suffix",
            "surname_override",
            "gender",
            "birthday",
            "email",
            "phone_mobile",
            "phone_work",
            "is_current",
        ]
        widgets = {"birthday": DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}


PersonInlineFormSet = inlineformset_factory(Family, Person, form=PersonForm, extra=1, can_delete=False)

FamilyForm = modelform_factory(
    Family,
    form=AdminFamilyForm,
    fields=[
        "name",
        "street",
        "suburb",
        "postcode",
        "phone_home",
        "phone_mobile",
        "email",
        "husband",
        "wife",
        "anniversary",
    ],
    widgets={"anniversary": DateInput(attrs={"type": "date"}, format="%Y-%m-%d")},
)
