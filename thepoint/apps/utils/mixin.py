from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_cookie


class NeverCacheMixin(object):
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(NeverCacheMixin, self).dispatch(*args, **kwargs)


class VaryOnCookieMixin(object):
    @method_decorator(vary_on_cookie)
    def dispatch(self, *args, **kwargs):
        return super(VaryOnCookieMixin, self).dispatch(*args, **kwargs)
