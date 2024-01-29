from django.test import TestCase

from hines.core.utils import markdownify, truncate_string


class MarkdownifyTestCase(TestCase):
    def test_basic(self):
        "Just test it actually does some Markdowning"
        html = markdownify("Hello\n\nBye")
        self.assertHTMLEqual(html, "<p>Hello</p>\n\n<p>Bye</p>\n")

    def test_fenced_code(self):
        "It should mark up fenced code blocks correctly."
        html = markdownify("```\nCode line 1\n\nCode line 2\n```")
        self.assertHTMLEqual(
            html, "<pre><code>Code line 1\n\nCode line 2\n</code></pre>\n"
        )

    def test_pygments_highlighting(self):
        "It should use pygments to highlight fenced code blocks"
        html = markdownify("```html\n<p>Hi</p>\n```")
        self.assertHTMLEqual(
            html,
            """<div class="codehilite">
                <pre>
                    <span></span>
                    <code>
                        <span class="p">&lt;</span>
                        <span class="nt">p</span>
                        <span class="p">&gt;</span>
                        Hi
                        <span class="p">&lt;/</span>
                        <span class="nt">p</span>
                        <span class="p">&gt;</span>
                    </code>
                </pre>
            </div>""",
        )

    def test_output_format_default(self):
        "By default it should produce XHTML-style tags"
        html = markdownify("Hi\n\n----\n\n![Alt](test.png)")
        self.assertHTMLEqual(
            html, '<p>Hi</p>\n\n<hr />\n\n<p><img src="test.png" alt="Alt" /></p>\n'
        )

    def test_output_format_xhtml(self):
        "It should produce XHTML-style tags when asked"
        # With trailing slashes on solo tags.
        html = markdownify("Hi\n\n----\n\n![Alt](test.png)", output_format="xhtml")
        self.assertHTMLEqual(
            html, '<p>Hi</p>\n\n<hr />\n\n<p><img src="test.png" alt="Alt" /></p>\n'
        )

    def test_output_format_html5(self):
        "It should produce HTML5-style tags when asked"
        # With NO trailing slashes on solo tags.
        html = markdownify("Hi\n\n----\n\n![Alt](test.png)", output_format="html5")
        self.assertHTMLEqual(
            html, '<p>Hi</p>\n\n<hr>\n\n<p><img src="test.png" alt="Alt"></p>\n'
        )

    def test_urls_to_links(self):
        "It should turn bare URLs into clickable links"
        html = markdownify("Hello https://www.example.org/foo/ Bye")
        self.assertHTMLEqual(
            html,
            (
                '<p>Hello <a href="https://www.example.org/foo/">'
                "https://www.example.org/foo/</a> Bye</p>\n"
            ),
        )

    def test_hrefs_are_untouched(self):
        "It should not do anything with links that are already clickable"
        text = (
            'Hello <a href="https://www.example.org/">https://www.example.org</a> Bye'
        )
        html = markdownify(text)
        self.assertEqual(html, f"<p>{text}</p>\n")

    def test_markdown_links_are_done_correctly(self):
        "Standard Markdown links should be linkified correctly"
        html = markdownify("Hello [Link](https://www.example.org/) Bye")
        self.assertHTMLEqual(
            html, '<p>Hello <a href="https://www.example.org/">Link</a> Bye</p>\n'
        )

    def test_markdown_strike(self):
        "Using ~~foo~~ should translate into <s>foo</s>"
        self.assertHTMLEqual(markdownify("~~foo~~"), "<p><s>foo</s></p>")

    def test_details(self):
        "It should render disclosures correctly"
        html = """<details>
<summary>Summary</summary>
Text inside.
</details>"""
        self.assertHTMLEqual(markdownify(html, output_format="html5"), html)

    def test_details_containing_html(self):
        "It should render disclosures containing HTML correctly"
        html = """<details>
<summary>Summary</summary>
<ul>
<li>Item 1</li>
<li>Item 2</li>
</ul>
</details>"""
        self.assertHTMLEqual(markdownify(html, output_format="html5"), html)


class TruncateStringTestCase(TestCase):
    def test_strip_html(self):
        "By default, strips HTML"
        self.assertEqual(
            truncate_string(
                "<p>Some text. "
                '<a href="http://www.example.com/"><b>A link</b></a>. And more.'
            ),
            "Some text. A link. And more.",
        )

    def test_strip_html_false(self):
        "Can be told not to strip HTML"
        self.assertEqual(
            truncate_string(
                "<p>Some text. "
                '<a href="http://www.example.com/"><b>A link</b></a>. And more.',
                strip_html=False,
            ),
            "<p>Some text. "
            '<a href="http://www.example.com/"><b>A link</b></a>. And more.',
        )

    def test_default_chars(self):
        "By default, trims to 255 characters"
        self.assertEqual(
            truncate_string(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eget "
                "odio eget odio porttitor accumsan in eget elit. Integer gravida "
                "egestas nunc. Mauris at tortor ornare, blandit eros quis, auctor "
                "lacus. Fusce ullamcorper nunc vitae tincidunt sodales. Vestibulum sit "
                "amet lacus at sem porta porta."
            ),
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eget "
            "odio eget odio porttitor accumsan in eget elit. Integer gravida "
            "egestas nunc. Mauris at tortor ornare, blandit eros quis, auctor "
            "lacus. Fusce ullamcorper nunc vitae tincidunt sodales. Ve…",
        )

    def test_custom_chars(self):
        "Can be told to truncate to other lengths"
        self.assertEqual(
            truncate_string(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eget "
                "odio eget odio porttitor accumsan in eget elit. Integer gravida "
                "egestas nunc. Mauris at tortor ornare, blandit eros quis, auctor "
                "lacus. Fusce ullamcorper nunc vitae tincidunt sodales. Vestibulum sit "
                "amet lacus at sem porta porta.",
                chars=100,
            ),
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eget "
            "odio eget odio porttitor accums…",
        )

    def test_truncate(self):
        "Can be given a custom 'truncate' string"
        self.assertEqual(
            truncate_string(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eget "
                "odio eget odio porttitor accumsan in eget elit. Integer gravida "
                "egestas nunc. Mauris at tortor ornare, blandit eros quis, auctor "
                "lacus. Fusce ullamcorper nunc vitae tincidunt sodales. Vestibulum sit "
                "amet lacus at sem porta porta.",
                truncate=" (cont.)",
            ),
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eget "
            "odio eget odio porttitor accumsan in eget elit. Integer gravida "
            "egestas nunc. Mauris at tortor ornare, blandit eros quis, auctor "
            "lacus. Fusce ullamcorper nunc vitae tincidunt soda (cont.)",
        )

    def test_at_word_boundary(self):
        "Will break at word boundaries."
        self.assertEqual(
            truncate_string(
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eget "
                "odio eget odio porttitor accumsan in eget elit. Integer gravida "
                "egestas nunc. Mauris at tortor ornare, blandit eros quis, auctor "
                "lacus. Fusce ullamcorper nunc vitae tincidunt sodales. Vestibulum sit "
                "amet lacus at sem porta porta.",
                at_word_boundary=True,
            ),
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eget "
            "odio eget odio porttitor accumsan in eget elit. Integer gravida "
            "egestas nunc. Mauris at tortor ornare, blandit eros quis, auctor "
            "lacus. Fusce ullamcorper nunc vitae tincidunt sodales.…",
        )

    def test_no_truncation(self):
        """Too short to be truncated."""
        self.assertEqual(truncate_string("This is my string."), "This is my string.")

    def test_no_truncation_at_word_boundary(self):
        """Too short to be truncated."""
        self.assertEqual(
            truncate_string("This is my string.", at_word_boundary=True),
            "This is my string.",
        )

    def test_all(self):
        """Will strip HTML, truncate to specified length, at a word boundary,
        and add custom string.
        """
        self.assertEqual(
            truncate_string(
                (
                    "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                    "Donec eget odio eget odio porttitor accumsan in eget elit. "
                    "Integer gravida egestas nunc. Mauris at tortor ornare, "
                    "blandit eros quis, auctorlacus.</p>"
                    "<p>Fusce ullamcorper nunc vitae tincidunt sodales. Vestibulum "
                    "sit amet lacus at sem porta porta. Donec fringilla laoreet orci "
                    "eu porta. Aenean non lacus hendrerit, semper odio a, feugiat "
                    "orci. Suspendisse potenti.</p>"
                ),
                strip_html=True,
                chars=200,
                truncate="...",
                at_word_boundary=True,
            ),
            (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec eget "
                "odio eget odio porttitor accumsan in eget elit. Integer gravida "
                "egestas nunc. Mauris at tortor ornare, blandit eros quis,..."
            ),
        )
