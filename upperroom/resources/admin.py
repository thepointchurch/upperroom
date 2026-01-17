from django.contrib import admin, auth
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ModelForm
from django.forms.widgets import Textarea
from django.utils import timezone
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

    @admin.display(description="")
    def drag_handle(self, obj):  # pylint: disable=unused-argument
        return ""


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

    @admin.display(description="")
    def drag_handle(self, obj):  # pylint: disable=unused-argument
        return ""


def _user_can_edit_own_only(user):
    if not user:
        return False
    if user.is_superuser:
        return False
    if not user.has_perm("resources.edit_own_resource"):
        return False
    return True


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

    def clean(self):
        # pubished timestamp will be set to now() if is_published is True in Resource.clean()
        # but we need to do it here first in case a slug prefix relies on it being set
        published = self.cleaned_data["published"]
        if self.cleaned_data.get("is_published") and published is None:
            published = timezone.now()
        prefix = self.instance.prefix_slug(
            set(self.cleaned_data["tags"].filter(slug_prefix__isnull=False).values_list("id", flat=True)),
            self.cleaned_data["slug"],
            published,
        )
        if prefix:
            self.cleaned_data["slug"] = prefix
            if Resource.objects.filter(slug=prefix).exists():
                self.add_error(
                    "slug",
                    _(
                        "%(model_name)s with this %(field_label)s already exists."
                        % {
                            "model_name": Resource._meta.verbose_name.title(),
                            "field_label": self.fields["slug"].label,
                        }
                    ),
                )
                raise ValidationError(_("Error applying defined Slug prefix"))
        return super().clean()


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


class OwnedResourceListFilter(admin.SimpleListFilter):
    title = _("ownership")
    parameter_name = "owner"

    def lookups(self, request, model_admin):
        lookups = [("self", _("Self"))]
        if request.user.is_superuser:
            lookups += [
                (user.id, user.get_full_name())
                for user in auth.get_user_model()
                .objects.filter(resources__isnull=False)
                .distinct()
                .only("last_name", "first_name")
                .order_by("last_name", "first_name", "username")
            ]
        return lookups

    def queryset(self, request, queryset):
        if self.value() == "self" and request.user:
            return queryset.filter(owner=request.user)
        if self.value():
            return queryset.filter(owner=self.value())
        return None


class ResourceAdmin(admin.ModelAdmin):
    model = Resource
    form = ResourceForm
    inlines = [AttachmentInline]
    ordering = ("title",)
    list_filter = [
        "tags",
        "created",
        "published",
        "modified",
        UnpublishedResourceListFilter,
        "is_private",
    ]
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
        (_("Publishing"), {"fields": ("is_published", "published")}),
        (_("Tags"), {"classes": ("collapse",), "fields": ("tags",)}),
        (_("Author"), {"classes": ("collapse",), "fields": ("author", "show_author")}),
        (_("Featured"), {"classes": ("collapse",), "fields": ("priority",)}),
        (
            _("Advanced"),
            {
                "classes": ("collapse",),
                "fields": ("owner", "is_private", "is_pinned", "show_date", "parent"),
            },
        ),
    )

    class Media:
        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.14.1/jquery-ui.min.js",
            "scripts/resources/admin_attachment_title.js",
            "scripts/resources/admin_dnd.js",
        )
        css = {"all": ("style/admin/resources.css",)}

    def get_inlines(self, request, obj):
        inlines = super().get_inlines(request, obj)
        if obj and obj.children.count() and ChildResourceInline not in inlines:
            inlines.append(ChildResourceInline)
        return inlines

    def get_list_filter(self, request):
        filter_list = super().get_list_filter(request)
        if not _user_can_edit_own_only(request.user):
            return filter_list + [OwnedResourceListFilter]
        return filter_list

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not _user_can_edit_own_only(request.user):
            return queryset
        if request.user:
            return queryset.filter(owner=request.user)
        return queryset.none()

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if not request.user.has_perm("resources.publish_resource"):
            fields += ("is_published",)
        if not request.user or not request.user.is_superuser:
            fields += ("owner",)
        return fields

    def save_model(self, request, obj, form, change):
        if not change and request.user:
            if not obj.owner or _user_can_edit_own_only(request.user):
                obj.owner = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description=_("Publish selected resources"))
    def publish(self, request, queryset):  # pylint: disable=unused-argument
        queryset.update(is_published=True)

    @admin.action(description=_("Unpublish selected resources"))
    def unpublish(self, request, queryset):  # pylint: disable=unused-argument
        queryset.update(is_published=False)

    @admin.action(description=_("Mark selected resources as private"))
    def mark_private(self, request, queryset):  # pylint: disable=unused-argument
        queryset.update(is_private=True)

    @admin.action(description=_("Mark selected resources as public"))
    def mark_public(self, request, queryset):  # pylint: disable=unused-argument
        queryset.update(is_private=False)


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
