from .models import get_featured_items


def featured_tags(request):
    context = {
        "featured_items": get_featured_items(),
    }

    if request.user.is_authenticated:
        context["featured_private_items"] = get_featured_items(True)

    return context
