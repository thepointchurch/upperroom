from django.contrib import admin
from django.db import models
from django.forms.widgets import Textarea
from django.utils.translation import ugettext_lazy as _

from .models import Attachment, Resource, Tag


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
                                    'show_date', 'is_exclusive')}),
    )


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ('mime_type',)
    prepopulated_fields = {'slug': ('title',)}
    formfield_overrides = {
        models.TextField: {'widget': Textarea(
                           attrs={'rows': 3,
                                  'cols': 40})},
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


class ResourceAdmin(admin.ModelAdmin):
    model = Resource
    inlines = [AttachmentInline]
    list_filter = ('tags', 'created', 'modified', 'is_published', 'is_private')
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
                         'fields': ('is_published', 'is_private', 'show_date',
                                    'parent')}),
    )


admin.site.register(Tag, TagAdmin)
admin.site.register(Resource, ResourceAdmin)
