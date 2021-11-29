import logging

from django.test import TestCase
from freezegun import freeze_time
from requests.exceptions import (
    RequestException,
    Timeout,
    TooManyRedirects,
)
import responses

from hines.core.utils import make_datetime
from hines.webmentions.factories import OutgoingWebmentionFactory
from hines.webmentions.models.models import OutgoingWebmention
from hines.webmentions.outgoing import send_outgoing_webmention
from tests import ResponsesMixin


# To save repetition:
DT = "2021-12-31 12:00:00"


def setUpModule():
    logging.disable(logging.WARNING)


def tearDownModule():
    logging.disable(logging.NOTSET)


class ProcessOutgoingWebmentionsTestcase(ResponsesMixin, TestCase):
    pass


@freeze_time(DT, tz_offset=0)
class SendOutgoingWebmentionsTestCase(ResponsesMixin, TestCase):

    target_url = "https://example.org/blog/1/"
    endpoint_url = "https://example.org/webmentions/"
    endpoint_headers = {"Link": f'<{endpoint_url}>; rel="webmention"'}

    def setUp(self):
        super().setUp()
        self.mention = OutgoingWebmentionFactory(target_url=self.target_url)

    # Testing errors when making a request to the Target URL.

    def test_target_timeout_exception(self):
        "If a Timeout happens, mention should be updated accordingly."
        responses.add(responses.GET, self.target_url, body=Timeout("Err"))

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "Target Timeout: Err")
        self.assertIsNone(self.mention.target_response_code)
        self.assertEqual(
            self.mention.status, OutgoingWebmention.Status.TARGET_UNREACHABLE
        )
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_target_too_many_redirects_exception(self):
        "If too many redirects, mention should be updated accordingly."
        responses.add(responses.GET, self.target_url, body=TooManyRedirects("Err"))

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "Target TooManyRedirects: Err")
        self.assertIsNone(self.mention.target_response_code)
        self.assertEqual(
            self.mention.status, OutgoingWebmention.Status.TARGET_UNREACHABLE
        )
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_target_request_exception(self):
        "If RequestException, mention should be updated accordingly."
        responses.add(responses.GET, self.target_url, body=RequestException("Err"))

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "Target RequestException: Err")
        self.assertIsNone(self.mention.target_response_code)
        self.assertEqual(
            self.mention.status, OutgoingWebmention.Status.TARGET_UNREACHABLE
        )
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_target_generic_exception(self):
        "If some other Exception, mention should be updated accordingly."
        responses.add(responses.GET, self.target_url, body=Exception("Err"))

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "Target Exception: Err")
        self.assertIsNone(self.mention.target_response_code)
        self.assertEqual(
            self.mention.status, OutgoingWebmention.Status.TARGET_UNREACHABLE
        )
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_target_500_response(self):
        "If 500 error, mention should be updated accordingly"
        responses.add(responses.GET, self.target_url, status=500)

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "")
        self.assertEqual(self.mention.target_response_code, 500)
        self.assertEqual(self.mention.status, OutgoingWebmention.Status.TARGET_ERROR)
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_target_404_response(self):
        "If 404 error, mention should be updated accordingly"
        responses.add(responses.GET, self.target_url, status=404)

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "")
        self.assertEqual(self.mention.target_response_code, 404)
        self.assertEqual(self.mention.status, OutgoingWebmention.Status.TARGET_ERROR)
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_target_300_response(self):
        "If 300 error, mention should be updated accordingly"
        responses.add(responses.GET, self.target_url, status=300)

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "")
        self.assertEqual(self.mention.target_response_code, 300)
        self.assertEqual(self.mention.status, OutgoingWebmention.Status.TARGET_ERROR)
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    # Testing errors when finding the Endpoint URL.

    def test_endpoint_timeout_exception(self):
        "If Timeout getting endpoint, mention should be updated accordingly"
        responses.add(responses.GET, self.target_url, headers=self.endpoint_headers)
        responses.add(responses.POST, self.endpoint_url, body=Timeout("Err"))

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "Endpoint Timeout: Err")
        self.assertIsNone(self.mention.endpoint_response_code)
        self.assertEqual(
            self.mention.status, OutgoingWebmention.Status.ENDPOINT_UNREACHABLE
        )
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_endpoint_too_many_redirects_exception(self):
        "If TooManyRedirects getting endpoint, mention should be updated accordingly"
        responses.add(responses.GET, self.target_url, headers=self.endpoint_headers)
        responses.add(responses.POST, self.endpoint_url, body=TooManyRedirects("Err"))

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "Endpoint TooManyRedirects: Err")
        self.assertIsNone(self.mention.endpoint_response_code)
        self.assertEqual(
            self.mention.status, OutgoingWebmention.Status.ENDPOINT_UNREACHABLE
        )
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_endpoint_request_exception(self):
        "If RequestException getting endpoint, mention should be updated accordingly"
        responses.add(responses.GET, self.target_url, headers=self.endpoint_headers)
        responses.add(responses.POST, self.endpoint_url, body=RequestException("Err"))

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "Endpoint RequestException: Err")
        self.assertIsNone(self.mention.endpoint_response_code)
        self.assertEqual(
            self.mention.status, OutgoingWebmention.Status.ENDPOINT_UNREACHABLE
        )
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_endpoint_generic_exception(self):
        "If Exception getting endpoint, mention should be updated accordingly"
        responses.add(responses.GET, self.target_url, headers=self.endpoint_headers)
        responses.add(responses.POST, self.endpoint_url, body=Exception("Err"))

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "Endpoint Exception: Err")
        self.assertIsNone(self.mention.endpoint_response_code)
        self.assertEqual(
            self.mention.status, OutgoingWebmention.Status.ENDPOINT_UNREACHABLE
        )
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_finding_endpoint_500_response(self):
        responses.add(responses.GET, self.target_url, headers=self.endpoint_headers)
        responses.add(responses.POST, self.endpoint_url, status=500)

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "")
        self.assertEqual(self.mention.endpoint_response_code, 500)
        self.assertEqual(self.mention.status, OutgoingWebmention.Status.ENDPOINT_ERROR)
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_finding_endpoint_404_response(self):
        responses.add(responses.GET, self.target_url, headers=self.endpoint_headers)
        responses.add(responses.POST, self.endpoint_url, status=404)

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "")
        self.assertEqual(self.mention.endpoint_response_code, 404)
        self.assertEqual(self.mention.status, OutgoingWebmention.Status.ENDPOINT_ERROR)
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_finding_endpoint_300_response(self):
        responses.add(responses.GET, self.target_url, headers=self.endpoint_headers)
        responses.add(responses.POST, self.endpoint_url, status=300)

        result = send_outgoing_webmention(self.mention)
        self.mention.refresh_from_db()

        self.assertFalse(result)
        self.assertEqual(self.mention.error_message, "")
        self.assertEqual(self.mention.endpoint_response_code, 300)
        self.assertEqual(self.mention.status, OutgoingWebmention.Status.ENDPOINT_ERROR)
        self.assertEqual(self.mention.last_attempt_time, make_datetime(DT))

    def test_endpoint_header_error(self):
        pass

    def test_endpoint_head_error(self):
        pass

    def test_endpoint_body_error(self):
        pass

    def test_endpoint_missing(self):
        pass

    # Testing successfully finding the endpoint URL

    def test_absolute_endpoint_url(self):
        pass

    def test_relative_endpoint_url(self):
        pass

    def test_relative_endpoint_url_missing_scheme(self):
        pass

    def test_relative_endpoint_url_missing_domain(self):
        pass

    def test_several_endpoint_links_in_head(self):
        "It should use the first link found"
        pass

    def test_several_endpoint_links_in_body(self):
        "It should use the first link found"
        pass

    # Testing sending the webmention to endpoint URL

    def test_sending_webmention_500_response(self):
        pass

    def test_sending_webmention_404_response(self):
        pass

    def test_sending_webmention_300_response(self):
        pass

    def test_sending_webmention_success(self):
        pass
