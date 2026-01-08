# pylint: disable=invalid-name

import re

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class EmbeddedVidProcessor(Treeprocessor):
    """Find "images" that are actually videos and use the appropriate tags."""

    def __init__(self, md):
        super().__init__()
        self.md = md

    @staticmethod
    def matchChildren(par):
        a = None
        img = par.find("./img")
        if img is None:
            a = par.find("./a")
            if a is not None:
                img = a.find("./img")
                if img is None:
                    a = None
        return (img, a)

    def run(self, root):
        for par in root.findall("./p"):
            img, _ = self.matchChildren(par)
            if img is None:
                continue
            if not img.tail or not re.match(r"^video/[a-z-]+", img.tail):
                continue
            par.tag = "video"
            par.set("controls", "")
            img.tag = "source"
            img.set("type", img.tail)
            img.tail = img.get("alt", "")
            del img.attrib["alt"]


class EmbeddedVidExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(EmbeddedVidProcessor(md), "vidembed", 9)


def makeExtension(**kwargs):
    return EmbeddedVidExtension(**kwargs)
