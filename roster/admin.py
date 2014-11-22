from django.contrib import admin

from roster.models import Meeting, Roster

class RosterInline(admin.TabularInline):
    model = Roster
    extra = 8
    exclude = ('revision',)

class MeetingAdmin(admin.ModelAdmin):
    inlines = [RosterInline]
    list_filter = ('date',)
    search_fields = ['date', 'roles__person__name', 'roles__person__family__name']

admin.site.register(Meeting, MeetingAdmin)
