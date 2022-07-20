from django.test import TestCase

from hines.custom_comments.utils import (
    clean_comment,
    get_allowed_attributes,
    get_allowed_tags,
)
from tests import override_app_settings


class CleanCommentTestCase(TestCase):
    @override_app_settings(COMMENTS_ALLOWED_TAGS=["b", "i", "a"])
    def test_strips_bad_tags(self):
        self.assertEqual(
            clean_comment('<h1>Heading</h1> <img src="blah"> Hello'), "Heading  Hello"
        )

    @override_app_settings(COMMENTS_ALLOWED_TAGS=["b", "i", "a"])
    def test_allows_good_tags(self):
        s = "<b>Bold</b> and <i>Italic</i>"
        self.assertEqual(clean_comment(s), s)

    @override_app_settings(COMMENTS_ALLOWED_TAGS=["b", "i", "a"])
    def test_closes_open_good_tags(self):
        self.assertEqual(clean_comment("<b>This is bold"), "<b>This is bold</b>")

    @override_app_settings(
        COMMENTS_ALLOWED_TAGS=["a"],
        COMMENTS_ALLOWED_ATTRIBUTES={"a": ["href", "title"]},
    )
    def test_allows_only_good_attributes(self):
        "Removes non-whitelisted attributes and adds rel=nofollow to a tags."
        self.assertHTMLEqual(
            clean_comment('<a href="foo" title="bar" id="bad">Link</a>'),
            '<a href="foo" rel="nofollow" title="bar">Link</a>',
        )

    def test_links_urls_http(self):
        "Turns URLs into links, removes protocol, and adds rel=nofollow."
        self.assertHTMLEqual(
            clean_comment("http://example.org/foo"),
            '<a href="http://example.org/foo" rel="nofollow">example.org/foo</a>',
        )

    def test_links_urls_https(self):
        "Turns https URLs into links, removes protocol, and adds rel=nofollow."
        self.assertHTMLEqual(
            clean_comment("https://example.org/foo"),
            '<a href="https://example.org/foo" rel="nofollow">example.org/foo</a>',
        )

    def test_truncates_long_urls(self):
        "Turns long URLs into truncated links and adds rel=nofollow."
        self.assertHTMLEqual(
            clean_comment("https://example.org/foo/bar/the_filename.html"),
            '<a href="https://example.org/foo/bar/the_filename.html" rel="nofollow">'
            "example.org/foo/bar/th…</a>",
        )

    def test_links_non_standard_tlds(self):
        "It should links URLs that contain one of the newer TLDs"
        self.assertHTMLEqual(
            clean_comment("https://www.example.blog/foo/bar/the_filename.html"),
            '<a href="https://www.example.blog/foo/bar/the_filename.html"'
            ' rel="nofollow">www.example.blog/foo/b…</a>',
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
    @override_app_settings(COMMENTS_ALLOWED_TAGS=["b", "i", "a"])
    def test_returns_settings_tags(self):
        "If set, it should return our custom setting."
        self.assertEqual(get_allowed_tags(), ["b", "i", "a"])


class GetAllowedAttributesTestCase(TestCase):
    @override_app_settings(COMMENTS_ALLOWED_ATTRIBUTES={"a": ["href", "title"]})
    def test_returns_settings_attributes(self):
        "If set, it should return our custom setting."
        self.assertEqual(get_allowed_attributes(), {"a": ["href", "title"]})
