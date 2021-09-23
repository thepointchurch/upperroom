from django.test import TestCase

from ...utils.markdown import unmarkdown


class TestMarkdownUnmarkdown(TestCase):
    def test_normal_paragraph(self):
        self.assertEqual(unmarkdown("Normal paragraph"), "Normal paragraph")

    def test_simple_formatting(self):
        self.assertEqual(unmarkdown("Just **simple** formatting"), "Just simple formatting")

    def test_multiple_paragraphs(self):
        self.assertEqual(unmarkdown("First paragraph\n\nSecond paragraph"), "First paragraph\nSecond paragraph")
