_SEARCHABLE_VIEWS = {}


def searchable(key: str):
    def decorator(cls):
        _SEARCHABLE_VIEWS[key] = cls
        return cls

    return decorator
