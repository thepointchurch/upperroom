from django import template

register = template.Library()


@register.filter
def remove_person(value, arg):
    return value.exclude(id__exact=arg.id)
