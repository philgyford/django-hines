from django.test import TestCase

from hines.custom_comments.utils import (
    clean_comment,
    get_allowed_attributes,
    get_allowed_tags,
)

from tests import override_app_settings


@override_app_settings(
    COMMENTS_ALLOWED_TAGS=["b", "i", "a"]
)
@override_app_settings(
    COMMENTS_ALLOWED_ATTRIBUTES={"a": ["href", "title"]}
)
class CleanCommentTestCase(TestCase):
    def test_strips_bad_tags(self):
        self.assertEqual(
            clean_comment('<h1>Heading</h1> <img src="blah"> Hello'), "Heading  Hello"
        )

    def test_allows_good_tags(self):
        s = "<b>Bold</b> and <i>Italic</i>"
        self.assertEqual(clean_comment(s), s)

    def test_closes_open_good_tags(self):
        self.assertEqual(clean_comment("<b>This is bold"), "<b>This is bold</b>")

    def test_allows_only_good_attributes(self):
        "Removes non-whitelisted attributes and adds rel=nofollow to a tags."
        self.assertEqual(
            clean_comment('<a href="foo" title="bar" id="bad">Link</a>'),
            '<a href="foo" rel="nofollow" title="bar">Link</a>',
        )

    def test_links_urls(self):
        "Turns URLs into links, removes protocol, and adds rel=nofollow."
        self.assertEqual(
            clean_comment("http://example.org/foo"),
            '<a href="http://example.org/foo" rel="nofollow">example.org/foo</a>',
        )

    def test_links_urls_https(self):
        "Turns https URLs into links, removes protocol, and adds rel=nofollow."
        self.assertEqual(
            clean_comment("https://example.org/foo"),
            '<a href="https://example.org/foo" rel="nofollow">example.org/foo</a>',
        )

    def test_truncates_long_urls(self):
        "Turns long URLs into truncated links and adds rel=nofollow."
        self.assertEqual(
            clean_comment("http://example.org/foo/bar/the_filename.html"),
            '<a href="http://example.org/foo/bar/the_filename.html" rel="nofollow">'
            "example.org/foo/bar/th…</a>",
        )

    def test_removes_extra_newlines(self):
        s1 = """First line.



Second line."""
        s2 = """First line.

Second line."""
        self.assertEqual(clean_comment(s1), s2)

    def test_strips_leading_and_trailing_space(self):
        self.assertEqual(clean_comment("   Hi   "), "Hi")


class GetAllowedTagsTestCase(TestCase):
    @override_app_settings(
        COMMENTS_ALLOWED_TAGS=["b", "i", "a"]
    )
    def test_returns_settings_tags(self):
        "If set, it should return our custom setting."
        self.assertEqual(get_allowed_tags(), ["b", "i", "a"])


class GetAllowedAttributesTestCase(TestCase):
    @override_app_settings(
        COMMENTS_ALLOWED_ATTRIBUTES={"a": ["href", "title"]}
    )
    def test_returns_settings_attributes(self):
        "If set, it should return our custom setting."
        self.assertEqual(get_allowed_attributes(), {"a": ["href", "title"]})
