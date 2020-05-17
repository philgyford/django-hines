from django.test import TestCase

from hines.blocks.factories import BlockFactory
from hines.blocks.templatetags.blocks import render_block


class RenderBlockTestCase(TestCase):
    def test_result_block_exists(self):
        block = BlockFactory(slug="my-block")
        result = render_block("my-block")
        self.assertEqual(result["block"], block)

    def test_result_block_does_not_exists(self):
        BlockFactory(slug="my-block")
        result = render_block("a-different-block")
        self.assertEqual(result, {})
