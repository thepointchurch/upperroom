from django.contrib import admin

from .models import ExtendedSite, Keyword


class KeywordInline(admin.TabularInline):
    model = Keyword
    extra = 0


class ExtendedSitesAdmin(admin.ModelAdmin):
    inlines = [KeywordInline]


admin.site.register(ExtendedSite, ExtendedSitesAdmin)
