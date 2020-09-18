from .models import Splash, get_splashes


def splashes(request):
    context = {
        "splashes_above": get_splashes(request, Splash.POSITION_ABOVE),
        "splashes_below": get_splashes(request, Splash.POSITION_BELOW),
    }

    return context
