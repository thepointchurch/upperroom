import re

_MIME_ANCHOR_MAP = {
    "audio": "listen",
    "video": "watch",
}


def get_mime_anchor(mime_type):
    return _MIME_ANCHOR_MAP.get(mime_type.split("/", maxsplit=1)[0])


def is_video_embed(body):
    video_embed = re.compile(r"<iframe [^>]+youtube[^>]+/embed/>")
    return bool([x for x in body.splitlines() if x and not video_embed.search(x)])
