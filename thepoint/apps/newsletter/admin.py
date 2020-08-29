from django.contrib import admin
from django.forms import ModelForm

from .models import Issue, Publication


class IssueForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        try:
            if self.instance.mime_type != cleaned_data["file"].content_type:
                self.instance.mime_type = cleaned_data["file"].content_type
        except AttributeError:
            # No new file was uploaded (cleaned_data['file'].content_type missing)
            pass

        return cleaned_data


class IssueAdmin(admin.ModelAdmin):
    model = Issue
    form = IssueForm
    list_filter = ("date", "publication")
    search_fields = ["date"]


admin.site.register(Publication)
admin.site.register(Issue, IssueAdmin)
