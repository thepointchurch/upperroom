import mimetypes

_preferred_types = {
    "audio/mp3": ".mp3",
    "image/jpeg": ".jpg",
    "text/plain": ".txt",
}

for type, ext in _preferred_types.items():  # pylint: disable=redefined-builtin
    mimetypes.add_type(type, ext)


def guess_extension(type, strict=True):  # pylint: disable=redefined-outer-name
    return _preferred_types.get(type) or mimetypes.guess_extension(type, strict)
