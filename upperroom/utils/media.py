import re

_MIME_ANCHOR_MAP = {
    "audio": "listen",
    "video": "watch",
}


def get_mime_anchor(mime_type):
    return _MIME_ANCHOR_MAP.get(mime_type.split("/", maxsplit=1)[0])


def is_video_embed(body):
    video_embed = re.compile(r"<iframe [^>]+youtube[^>]+/embed/")
    lines = [x for x in body.splitlines() if x]
    non_embed_lines = [x for x in lines if not video_embed.search(x)]
    return len(lines) != len(non_embed_lines)
