from io import StringIO

from markdown import Markdown


def __unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        __unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


# patching Markdown
Markdown.output_formats["plain"] = __unmark_element
__md = Markdown(output_format="plain")
__md.stripTopLevelTags = False


def unmarkdown(text):
    return __md.convert(text)
