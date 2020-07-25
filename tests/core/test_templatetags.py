from unittest.mock import patch

from freezegun import freeze_time

from django.test import TestCase

from hines.core.templatetags.hines_core import (
    gravatar_url,
    get_item,
    display_time,
    smartypants,
    widont,
    linebreaks_first,
    domain_urlize,
)
from hines.core.utils import make_datetime

from tests import override_app_settings


class GravatarURLTestcase(TestCase):
    def test_returns_url(self):
        "It should return the correct URL for a lowercased, stripped email"
        url = gravatar_url(" PHIL@gyford.com  ")
        self.assertEqual(
            url,
            (
                "https://secure.gravatar.com/avatar/"
                "57d9e4faebab769718a0b4107c3d06df.jpg?d=mp&size=80"
            ),
        )

    def returns_empty_string(self):
        "It should return empty string if the stripped email is empty"
        url = gravatar_url("     ")
        self.assertEqual(url, "")


class GetItemTestCase(TestCase):
    def test_returns_value(self):
        ages = {"bob": 37}
        self.assertEqual(get_item(ages, "bob"), 37)

    def test_returns_None(self):
        ages = {"bob": 37}
        self.assertIsNone(get_item(ages, "amy"))


class DisplayTimeTestCase(TestCase):
    @override_app_settings(DATE_FORMAT="%-d %b %Y", DATETIME_FORMAT="[time] on [date]")
    def test_returns_datetime_by_default(self):
        self.assertEqual(
            display_time(make_datetime("2015-08-14 13:34:56")),
            '<time datetime="2015-08-14 13:34:56">13:34 on 14 Aug 2015</time>',
        )

    @override_app_settings(DATE_FORMAT="%-d %b %Y", DATETIME_FORMAT="[time] on [date]")
    @freeze_time("2015-08-14 13:34:56", tz_offset=0)
    def test_uses_now_if_no_datetime_supplied(self):
        self.assertEqual(
            display_time(),
            '<time datetime="2015-08-14 13:34:56">13:34 on 14 Aug 2015</time>',
        )

    @override_app_settings(DATE_FORMAT="%-d %b %Y", DATETIME_FORMAT="[time] on [date]")
    def test_returns_datetime(self):
        self.assertEqual(
            display_time(make_datetime("2015-08-14 13:34:56"), show="both"),
            '<time datetime="2015-08-14 13:34:56">13:34 on 14 Aug 2015</time>',
        )

    @override_app_settings(DATE_FORMAT="%-d %b %Y")
    def test_returns_date(self):
        self.assertEqual(
            display_time(make_datetime("2015-08-14 13:34:56"), show="date"),
            '<time datetime="2015-08-14 13:34:56">14 Aug 2015</time>',
        )

    def test_returns_time(self):
        self.assertEqual(
            display_time(make_datetime("2015-08-14 13:34:56"), show="time"),
            '<time datetime="2015-08-14 13:34:56">13:34</time>',
        )

    @override_app_settings(DATE_FORMAT="%-d %b %Y", DATETIME_FORMAT="[time] on [date]")
    @patch("hines.core.templatetags.hines_core.reverse")
    def test_returns_datetime_with_link(self, reverse):
        reverse.return_value = "/2015/08/14/"
        self.assertEqual(
            display_time(
                make_datetime("2015-08-14 13:34:56"), show="both", link_to_day=True
            ),
            '<time datetime="2015-08-14 13:34:56">13:34 on <a href="/2015/08/14/" title="All items from this day">14 Aug 2015</a></time>',  # noqa: E501
        )

    @override_app_settings(DATE_FORMAT="%-d %b %Y")
    @patch("hines.core.templatetags.hines_core.reverse")
    def test_returns_date_with_link(self, reverse):
        reverse.return_value = "/2015/08/14/"
        self.assertEqual(
            display_time(
                make_datetime("2015-08-14 13:34:56"), show="date", link_to_day=True
            ),
            '<time datetime="2015-08-14 13:34:56"><a href="/2015/08/14/" title="All items from this day">14 Aug 2015</a></time>',  # noqa: E501
        )

    def test_returns_time_with_no_link(self):
        "Link isn't added if show='time' even if link_to_day=True."
        self.assertEqual(
            display_time(
                make_datetime("2015-08-14 13:34:56"), show="time", link_to_day=True
            ),
            '<time datetime="2015-08-14 13:34:56">13:34</time>',
        )


class SmartypantsTestCase(TestCase):
    def test_smartypants(self):
        self.assertEqual(
            smartypants("""This... isn't -- "special"."""),
            "This&#8230; isn&#8217;t &#8212; &#8220;special&#8221;.",
        )


class WidontTestCase(TestCase):
    "From https://github.com/chrisdrackett/django-typogrify"

    def test_simple(self):
        self.assertEqual(widont("A very simple test"), "A very simple&nbsp;test")

    def test_single_word(self):
        self.assertEqual(widont("Test"), "Test")

    def test_single_word_leading_space(self):
        self.assertEqual(widont(" Test"), " Test")

    def test_html(self):
        self.assertEqual(
            widont("<ul><li>Test</p></li><ul>"), "<ul><li>Test</p></li><ul>"
        )

    def test_html_leading_space(self):
        self.assertEqual(
            widont("<ul><li> Test</p></li><ul>"), "<ul><li> Test</p></li><ul>"
        )

    def test_two_paragraphs(self):
        self.assertEqual(
            widont("<p>In a couple of paragraphs</p><p>paragraph two</p>"),
            "<p>In a couple of&nbsp;paragraphs</p><p>paragraph&nbsp;two</p>",
        )

    def test_link_in_heading(self):
        self.assertEqual(
            widont('<h1><a href="#">In a link inside a heading</i> </a></h1>'),
            '<h1><a href="#">In a link inside a&nbsp;heading</i> </a></h1>',
        )

    def test_link_followed_by_other_text(self):
        self.assertEqual(
            widont('<h1><a href="#">In a link</a> followed by other text</h1>'),
            '<h1><a href="#">In a link</a> followed by other&nbsp;text</h1>',
        )

    def test_empty_html(self):
        "Shouldn't error"
        self.assertEqual(
            widont('<h1><a href="#"></a></h1>'), '<h1><a href="#"></a></h1>'
        )

    def test_div(self):
        "Shouldn't work in <div>s"
        self.assertEqual(
            widont("<div>Divs get no love!</div>"), "<div>Divs get no love!</div>"
        )

    def test_pre(self):
        "Shouldn't work in <pre>s"
        self.assertEqual(
            widont("<pre>Neither do PREs</pre>"), "<pre>Neither do PREs</pre>"
        )

    def test_paragraph_in_div(self):
        "Should work here"
        self.assertEqual(
            widont("<div><p>But divs with paragraphs do!</p></div>"),
            "<div><p>But divs with paragraphs&nbsp;do!</p></div>",
        )


class LinebreaksFirstTestCase(TestCase):
    def test_linebreaks_first(self):
        self.assertEqual(
            linebreaks_first("This is the\nfirst par.\n\nAnd a second."),
            """<p class="first">This is the<br>first par.</p>\n\n<p>And a second.</p>""",  # noqa: E501
        )


class DomainUrlizeTestCase(TestCase):
    def test_domain_urlize(self):
        self.assertEqual(
            domain_urlize("http://www.example.org/foo/"),
            '<a href="http://www.example.org/foo/" rel="nofollow">example.org</a>',
        )
