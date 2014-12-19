from django.contrib import admin

from library.models import Book


class BookAdmin(admin.ModelAdmin):
    list_filter = ('type', 'location')
    search_fields = ['title', 'subtitle', 'description', 'author', 'isbn']

admin.site.register(Book, BookAdmin)
