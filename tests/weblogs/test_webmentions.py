from django.test import Client, TestCase

from hines.core.utils import make_datetime
from hines.weblogs.factories import BlogFactory, LivePostFactory


class WebmentionsTestCase(TestCase):
    def test_webmentions_endpoint_with_valid_post_url(self):
        "It should return the Post target url if the Post exists"
        LivePostFactory(
            blog=BlogFactory(slug="my-blog"),
            slug="my-post",
            time_published=make_datetime("2022-02-01 23:59:59"),
        )

        response = Client().get(
            "/webmentions/get/", {"url": "/terry/my-blog/2022/02/01/my-post/"}
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertNotIn("message", data)
        self.assertEqual(
            data["target_url"], "http://testserver/terry/my-blog/2022/02/01/my-post/"
        )
        self.assertEqual(data["mentions"], [])

    # def test_webmentions_endpoint_with_invalid_post_url(self):
    #     "It should raise 404 if no matching post is found"
    #     response = Client().get(
    #         "/webmentions/get/", {"url": "/terry/blog/1111/11/11/post/"}
    #     )
    #     self.assertEqual(response.status_code, 404)

    def test_webmentions_endpoint_in_post_detail_template(self):
        "The endpoint should be linked to in the HTML"
        p = LivePostFactory()
        response = Client().get(p.get_absolute_url())
        self.assertInHTML(
            '<link rel="webmention" href="/webmentions/" />', response.content.decode()
        )
