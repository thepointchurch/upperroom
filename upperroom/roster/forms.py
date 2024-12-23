# pylint: disable=modelform-uses-exclude

from django import forms
from django.db.models import F, Max, Q

from .models import Meeting, Role


class MeetingBuilderRoleForm(forms.ModelForm):
    class Meta:
        model = Role
        exclude = ()
        widgets = {"role": forms.HiddenInput()}

    def __init__(self, sort_by_age=True, **kwargs):
        super().__init__(**kwargs)
        if not self.is_bound:
            self.role_type = self.initial["role"]
            if sort_by_age and self.role_type.order_by_age:
                qs = (
                    self.role_type.servers.select_related("family")
                    .annotate(
                        age=Max(
                            "roles__meeting__date",
                            filter=Q(roles__role=self.role_type)
                            | (Q(roles__role__parent__isnull=False) & Q(roles__role__parent=self.role_type.parent)),
                        )
                    )
                    .order_by(F("age").asc(nulls_first=True), "name")
                )
            else:
                qs = self.role_type.servers.order_by("family__name", "name").select_related("family")
            self.fields["people"].queryset = qs


def meetingbuilderformset_factory(role_count=0):
    return forms.models.inlineformset_factory(
        Meeting,
        Role,
        form=MeetingBuilderRoleForm,
        fields=["people", "guest", "role", "description"],
        can_delete=False,
        extra=role_count,
    )
