from django.contrib import admin
from django.db import models
from django.forms import ModelForm
from django.forms.widgets import Textarea
from django.utils.translation import gettext_lazy as _

from .models import Attachment, Resource, ResourceFeed, Tag
from ..directory.models import Person


class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_filter = ('name', 'is_exclusive')
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'description')}),
        (_('Featured'), {'classes': ('collapse',),
                         'fields': ('priority',)}),
        (_('Advanced'), {'classes': ('collapse',),
                         'fields': ('resources_per_page', 'reverse_order',
                                    'show_date', 'is_exclusive', 'is_private')}),
    )


class AttachmentForm(ModelForm):
    def clean(self):
        cleaned_data = super(AttachmentForm, self).clean()

        try:
            if self.instance.mime_type != cleaned_data['file'].content_type:
                self.instance.mime_type = cleaned_data['file'].content_type
        except (AttributeError, KeyError):
            # No new file was uploaded (cleaned_data['file'] missing)
            pass

        return cleaned_data


class AttachmentInline(admin.TabularInline):
    model = Attachment
    form = AttachmentForm
    extra = 0
    readonly_fields = ('mime_type',)
    prepopulated_fields = {'slug': ('title',)}
    fields = ('file', 'title', 'slug', 'kind', 'description', 'metadata', 'mime_type')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(
                           attrs={'rows': 3,
                                  'cols': 40})},
        models.JSONField: {'widget': Textarea(
                           attrs={'rows': 3,
                                  'cols': 20})},
    }


def action_publish(modeladmin, request, queryset):
    queryset.update(is_published=True)


action_publish.short_description = _('Publish selected resources')


def action_unpublish(modeladmin, request, queryset):
    queryset.update(is_published=False)


action_unpublish.short_description = _('Unpublish selected resources')


def action_mark_private(modeladmin, request, queryset):
    queryset.update(is_private=True)


action_mark_private.short_description = _('Mark selected resources as private')


def action_mark_public(modeladmin, request, queryset):
    queryset.update(is_private=False)


action_mark_public.short_description = _('Mark selected resources as public')


class ResourceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ResourceForm, self).__init__(*args, **kwargs)
        if self.instance.author:
            self.fields['author'].queryset = (
                Person.objects.filter(models.Q(id__exact=self.instance.author.id) |
                                      (models.Q(is_current=True) & models.Q(is_member=True)))
            )
        else:
            self.fields['author'].queryset = (
                Person.objects.filter(models.Q(is_current=True) & models.Q(is_member=True))
            )


class ResourceAdmin(admin.ModelAdmin):
    model = Resource
    form = ResourceForm
    inlines = [AttachmentInline]
    ordering = ('title',)
    list_filter = ('tags', 'created', 'published', 'modified', 'is_published', 'is_private')
    search_fields = ['title', 'description', 'body']
    prepopulated_fields = {'slug': ('title',)}
    actions = [action_publish, action_unpublish,
               action_mark_private, action_mark_public]

    fieldsets = (
        (None, {'fields': ('title', 'slug', 'description', 'body')}),
        (_('Tags'), {'classes': ('collapse',),
                     'fields': ('tags',)}),
        (_('Author'), {'classes': ('collapse',),
                       'fields': ('author', 'show_author')}),
        (_('Featured'), {'classes': ('collapse',),
                         'fields': ('priority',)}),
        (_('Advanced'), {'classes': ('collapse',),
                         'fields': ('is_published', 'published', 'is_private', 'show_date',
                                    'parent')}),
    )


class ResourceFeedAdmin(admin.ModelAdmin):
    model = ResourceFeed
    list_filter = ('is_podcast',)
    search_fields = ['title']
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        (None, {'fields': ('title', 'slug', 'description')}),
        (_('Optional'), {'classes': ('collapse',),
                         'fields': ('tags', 'show_children', 'mime_type_list', 'category_list', 'copyright')}),
        (_('Podcast'), {'classes': ('collapse',),
                        'fields': ('is_podcast', 'artwork', 'owner_name', 'owner_email')}),
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceFeed, ResourceFeedAdmin)
