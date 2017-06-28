from django.contrib import admin

from splash.models import Splash


class SplashAdmin(admin.ModelAdmin):
    list_filter = ('is_current', 'is_private', 'position')
    search_fields = ['title', 'content']


admin.site.register(Splash, SplashAdmin)
