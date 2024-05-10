from django.contrib import admin
from django.db import models
from django.forms import ModelForm
from django.forms.widgets import Textarea
from django.utils.translation import gettext_lazy as _

from ..directory.models import Person
from .models import Attachment, Resource, ResourceFeed, Tag


class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_filter = ("name", "is_exclusive")
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}

    fieldsets = (
        (None, {"fields": ("name", "slug", "description")}),
        (_("Featured"), {"classes": ("collapse",), "fields": ("priority",)}),
        (
            _("Advanced"),
            {
                "classes": ("collapse",),
                "fields": (
                    "resources_per_page",
                    "reverse_order",
                    "show_date",
                    "slug_prefix",
                    "is_exclusive",
                    "is_private",
                ),
            },
        ),
    )


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
    fields = ("drag_handle", "file", "title", "slug", "kind", "description", "metadata", "mime_type")
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 3, "cols": 40})},
        models.JSONField: {"widget": Textarea(attrs={"rows": 3, "cols": 20})},
    }
    classes = ("attachments",)

    def drag_handle(self, obj):  # pylint: disable=unused-argument
        return ""

    drag_handle.short_description = ""


class ChildResourceInline(admin.TabularInline):
    model = Resource
    fk_name = "parent"
    readonly_fields = ("drag_handle",)
    fields = ("drag_handle", "title", "slug")
    verbose_name = "children"
    verbose_name_plural = "children"
    view_on_site = False
    extra = 0
    max_num = 0
    classes = ("children",)

    def has_add_permission(self, request, obj=None):  # pylint: disable=unused-argument
        return False

    def has_change_permission(self, request, obj=None):  # pylint: disable=unused-argument
        return False

    def has_delete_permission(self, request, obj=None):  # pylint: disable=unused-argument
        return False

    def drag_handle(self, obj):  # pylint: disable=unused-argument
        return ""

    drag_handle.short_description = ""


class ResourceForm(ModelForm):
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


class UnpublishedResourceListFilter(admin.SimpleListFilter):
    title = _("published")
    parameter_name = "published"

    def lookups(self, request, model_admin):
        lookups = (("yes", _("Yes")), ("no", _("No")))
        if request.user.has_perm("resources.publish_resource"):
            lookups += (("pending", _("Pending")),)
        return lookups

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(is_published=True)
        if self.value() == "no":
            return queryset.filter(is_published=False)
        if self.value() == "pending" and request.user.has_perm("resources.publish_resource"):
            return queryset.filter(is_published=False, published__isnull=True)
        return None


class ResourceAdmin(admin.ModelAdmin):
    model = Resource
    form = ResourceForm
    inlines = [AttachmentInline]
    ordering = ("title",)
    list_filter = (
        "tags",
        "created",
        "published",
        "modified",
        UnpublishedResourceListFilter,
        "is_private",
    )
    search_fields = ["title", "description", "body"]
    date_hierarchy = "published"
    prepopulated_fields = {"slug": ("title",)}
    actions = ["publish", "unpublish", "mark_private", "mark_public"]

    fieldsets = (
        (
            None,
            {
                "fields": ("title", "slug", "description", "body"),
                "description": _(
                    "<dl>"
                    "<dt>To insert inline links:</dt>"
                    "<dd><code>[text][slug]</code></dd>"
                    "<dt>To insert inline images:</dt>"
                    "<dd><code>![alt][slug]</code></dd>"
                    "</dl>"
                    "<p>Images should be in their own paragraph, separated by blank lines.</p>"
                    "<p>You can also drag-and-drop attachments and child resources "
                    "to insert links at the current cursor point.</p>"
                ),
            },
        ),
        (_("Tags"), {"classes": ("collapse",), "fields": ("tags",)}),
        (_("Author"), {"classes": ("collapse",), "fields": ("author", "show_author")}),
        (_("Featured"), {"classes": ("collapse",), "fields": ("priority",)}),
        (
            _("Advanced"),
            {
                "classes": ("collapse",),
                "fields": ("is_published", "published", "is_private", "is_pinned", "show_date", "parent"),
            },
        ),
    )

    class Media:
        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js",
            "scripts/resources/admin_attachment_title.js",
            "scripts/resources/admin_dnd.js",
        )
        css = {"all": ("style/admin/resources.css",)}

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        if obj and obj.children.count() and ChildResourceInline not in inlines:
            inlines.append(ChildResourceInline)
        return inlines

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if not request.user.has_perm("resources.publish_resource"):
            fields += ("is_published",)
        return fields

    def publish(self, request, queryset):  # pylint: disable=unused-argument
        queryset.update(is_published=True)

    publish.short_description = _("Publish selected resources")

    def unpublish(self, request, queryset):  # pylint: disable=unused-argument
        queryset.update(is_published=False)

    unpublish.short_description = _("Unpublish selected resources")

    def mark_private(self, request, queryset):  # pylint: disable=unused-argument
        queryset.update(is_private=True)

    mark_private.short_description = _("Mark selected resources as private")

    def mark_public(self, request, queryset):  # pylint: disable=unused-argument
        queryset.update(is_private=False)

    mark_public.short_description = _("Mark selected resources as public")


class ResourceFeedAdmin(admin.ModelAdmin):
    model = ResourceFeed
    list_filter = ("is_podcast",)
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}

    fieldsets = (
        (None, {"fields": ("title", "slug", "description")}),
        (
            _("Optional"),
            {
                "classes": ("collapse",),
                "fields": ("tags", "show_children", "mime_type_list", "category_list", "copyright"),
            },
        ),
        (_("Podcast"), {"classes": ("collapse",), "fields": ("is_podcast", "artwork", "owner_name", "owner_email")}),
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceFeed, ResourceFeedAdmin)
