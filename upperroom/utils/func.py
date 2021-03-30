from django.db.models import BooleanField, Func


class IsNull(Func):  # pylint: disable=abstract-method
    _output_field = BooleanField()
    arity = 1
    template = "%(expressions)s IS NULL"


class IsNotNull(Func):  # pylint: disable=abstract-method
    _output_field = BooleanField()
    arity = 1
    template = "%(expressions)s IS NOT NULL"


class IsEmpty(Func):  # pylint: disable=abstract-method
    _output_field = BooleanField()
    arity = 1
    template = "(%(expressions)s IS NULL OR %(expressions)s = '')"


class IsNotEmpty(Func):  # pylint: disable=abstract-method
    _output_field = BooleanField()
    arity = 1
    template = "(%(expressions)s IS NOT NULL AND %(expressions)s != '')"
