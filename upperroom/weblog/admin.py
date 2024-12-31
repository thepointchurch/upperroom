from django.contrib import admin
from django.db import models
from django.forms import ModelForm
from django.forms.widgets import Textarea
from django.utils.translation import gettext_lazy as _

from ..directory.models import Person
from .models import Attachment, WeblogEntry


class AttachmentForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()

        try:
            if self.instance.mime_type != cleaned_data["file"].content_type:
                self.instance.mime_type = cleaned_data["file"].content_type
        except (AttributeError, KeyError):
            # No new file was uploaded (cleaned_data['file'] missing)
            pass

        return cleaned_data


class AttachmentInline(admin.StackedInline):
    model = Attachment
    form = AttachmentForm
    extra = 0
    readonly_fields = (
        "drag_handle",
        "mime_type",
    )
    prepopulated_fields = {"slug": ("title",)}
    fields = ("drag_handle", "file", "title", "slug", "kind", "description", "mime_type")
    ordering = ("title", "slug")
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 3, "cols": 40})},
    }

    def drag_handle(self, obj):  # pylint: disable=unused-argument
        return ""

    drag_handle.short_description = ""


class WeblogEntryForm(ModelForm):
    class Meta:
        labels = {
            "published": _("Published Timestamp"),
            "description": _("Short Body"),
            "body": _("Long Body"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.author:
            self.fields["author"].queryset = Person.objects.filter(
                models.Q(id__exact=self.instance.author.id) | (models.Q(is_current=True) & models.Q(is_member=True))
            ).order_by("family__name", "name")
        else:
            self.fields["author"].queryset = Person.objects.filter(
                models.Q(is_current=True) & models.Q(is_member=True)
            ).order_by("family__name", "name")


class WeblogAdmin(admin.ModelAdmin):
    model = WeblogEntry
    form = WeblogEntryForm
    inlines = [AttachmentInline]
    list_filter = ("created", "published", "modified", "is_published")
    search_fields = ["title", "description", "body"]
    date_hierarchy = "published"
    prepopulated_fields = {"slug": ("title",)}
    actions = ["publish", "unpublish"]
    readonly_fields = ("created", "modified")

    fieldsets = (
        (
            None,
            {
                "fields": ("title", "slug", "description", "body", "is_published"),
                "description": _(
                    "<dl>"
                    "<dt>To insert inline links:</dt>"
                    "<dd><code>[text][slug]</code></dd>"
                    "<dt>To insert inline images:</dt>"
                    "<dd><code>![alt][slug]</code></dd>"
                    "</dl>"
                    "<p>Images should be in their own paragraph, separated by blank lines.</p>"
                    "<p>You can also drag-and-drop attachments to insert links at the current cursor point.</p>"
                ),
            },
        ),
        (_("Timestamps"), {"classes": ("collapse",), "fields": ("published", "created", "modified")}),
        (_("Advanced"), {"classes": ("collapse",), "fields": ("show_date", "show_author", "author")}),
    )

    class Media:
        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.14.1/jquery-ui.min.js",
            "scripts/weblog/admin_attachment_title.js",
            "scripts/weblog/admin_dnd.js",
        )
        css = {"all": ("style/admin/weblog.css",)}

    def get_changeform_initial_data(self, request):
        get_data = super().get_changeform_initial_data(request)
        try:
            get_data["author"] = request.user.person
        except Person.DoesNotExist:
            pass
        return get_data

    def publish(self, request, queryset):  # pylint: disable=unused-argument
        queryset.update(is_published=True)

    publish.short_description = _("Publish selected " + str(WeblogEntry._meta.verbose_name_plural))

    def unpublish(self, request, queryset):  # pylint: disable=unused-argument
        queryset.update(is_published=False)

    unpublish.short_description = _("Unpublish selected " + str(WeblogEntry._meta.verbose_name_plural))


admin.site.register(WeblogEntry, WeblogAdmin)
