import re
from collections import deque
from itertools import islice
from typing import Any

from markdown import Markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


def sliding_window(iterable, n):
    # https://docs.python.org/3/library/itertools.html
    iterator = iter(iterable)
    window = deque(islice(iterator, n - 1), maxlen=n)
    for x in iterator:
        window.append(x)
        yield tuple(window)


class EmbeddedYoutubeProcessor(Preprocessor):  # pylint: disable=too-few-public-methods
    """Find lines that contain just a single YouTube URL and turn it into an embed."""

    def __init__(self, md: Markdown, config: dict[str, Any]):
        super().__init__(md)
        self.re = re.compile(
            r"https?://(?:www\.)?(?:"
            + "|".join(domain.replace(".", r"\.") for domain in config.get("domains", []))
            + r")/(?:watch\?v=)?([\-_a-zA-Z0-9]{11})"
        )
        self.format = config.get("format", "")

    def run(self, lines):
        new_lines = []
        previous_line = ""
        # use the sliding window to make sure the lines before and after are empty
        for line, next_line in sliding_window(lines, 2):
            if (previous_line, next_line) == ("", ""):
                if match := self.re.match(line):
                    line = self.format.format(vid=match.group(1))
            new_lines.append(line)

            previous_line = line

        return new_lines


class EmbeddedYoutubeExtension(Extension):  # pylint: disable=too-few-public-methods
    _DEFAULT_DOMAINS = ["youtube.com", "youtu.be"]
    _DEFAULT_FORMAT = (
        '<div style="margin: 1em; text-align: center">'
        '<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/{vid}?rel=0"'
        ' referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
    )

    def __init__(self, **kwargs):
        self.config = {
            "domains": [self._DEFAULT_DOMAINS, "YouTube domains to match."],
            "format": [self._DEFAULT_FORMAT, "Embed code format."],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md):  # pylint: disable=invalid-name
        md.registerExtension(self)
        md.preprocessors.register(EmbeddedYoutubeProcessor(md, self.getConfigs()), "yt", 10)


def makeExtension(**kwargs):  # pylint: disable=invalid-name
    return EmbeddedYoutubeExtension(**kwargs)
