# pylint: disable=invalid-name

import re
import xml.etree.ElementTree as ET

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


class EmbeddedMediaProcessor(Treeprocessor):
    """Find "images" that are actually audio or video and use the appropriate tags."""

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
            if not img.tail:
                continue
            mime_match = re.match(r"^(audio|video)/[a-z-]+", img.tail)
            if not mime_match:
                continue

            # retask the <p> element as our outer <div>
            par.tag = "div"
            par.set("class", "media")

            # create the new media element
            media = ET.Element(mime_match.group(1))
            media.set("controls", "")
            par.append(media)

            # retask the <img> element as our <source> element
            img.tag = "source"
            img.set("type", img.tail)
            img.tail = img.get("alt", "")
            del img.attrib["alt"]

            # insert the media element between the <div> and the <source> elements
            par.remove(img)
            media.append(img)


class EmbeddedMediaExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(EmbeddedMediaProcessor(md), "mediaembed", 9)


def makeExtension(**kwargs):
    return EmbeddedMediaExtension(**kwargs)
