from django.test import TestCase

from hines.blocks.factories import BlockFactory


class BlockTestCase(TestCase):
    def test_str_with_title(self):
        block = BlockFactory(slug="my-block", title="My block")
        self.assertEqual(str(block), "My block")

    def test_str_with_no_title(self):
        block = BlockFactory(slug="my-block", title="")
        self.assertEqual(str(block), "my-block")

    def test_content_html(self):
        "It should convert markdown to html."
        block = BlockFactory(
            content="""[Hello](http://example.org).  \n*Another* line."""
        )
        self.assertEqual(
            block.content_html,
            '<p><a href="http://example.org">Hello</a>.<br />\n'
            "<em>Another</em> line.</p>",
        )
