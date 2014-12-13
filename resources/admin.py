from django.contrib import admin
from django.db import models
from django.forms.widgets import Textarea

from resources.models import Attachment, Resource, Tag


class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_filter = ('name', 'is_exclusive')
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    readonly_fields = ('mime_type',)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(
                           attrs={'rows': 3,
                                  'cols': 40})},
    }


class ResourceAdmin(admin.ModelAdmin):
    model = Resource
    inlines = [AttachmentInline]
    list_filter = ('tags', 'created', 'modified', 'is_published', 'is_private')
    search_fields = ['title', 'description', 'body']
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        (None, {'fields': ('title', 'slug', 'description', 'body')}),
        ('Tags', {'classes': ('collapse',),
                  'fields': ('tags',)}),
        ('Author', {'classes': ('collapse',),
                    'fields': ('author', 'show_author')}),
        ('Advanced', {'classes': ('collapse',),
                      'fields': ('is_published', 'is_private',)}),
    )

admin.site.register(Tag, TagAdmin)
admin.site.register(Resource, ResourceAdmin)
