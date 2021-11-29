import logging
import re
from typing import Optional
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils import timezone
import requests

from .models import OutgoingWebmention


log = logging.getLogger(__name__)

# A lot of this from
# https://github.com/beatonma/django-wm/blob/master/mentions/tasks/outgoing_webmentions.py


def process_outgoing_webmentions():
    """ """
    sent_count = 0
    success_count = 0

    mentions = OutgoingWebmention.objects.filter(
        status=OutgoingWebmention.Status.WAITING
    )

    for mention in mentions:
        sent_count += 1
        result = send_outgoing_webmention(mention)
        if result:
            success_count += 1

    return {
        "sent": sent_count,
        "success": success_count,
        "errors": (sent_count - success_count),
    }


def send_outgoing_webmention(mention):

    mention.error_message = ""
    mention.response_code = None
    mention.last_attempt_time = timezone.now()

    is_success = False

    log.info("Sending outgoing webmention: {mention.target_url}")

    try:
        response = requests.get(mention.target_url, timeout=10)
    except requests.exceptions.Timeout as e:
        mention.error_message = f"Target Timeout: {e}"
    except requests.exceptions.TooManyRedirects as e:
        mention.error_message = f"Target TooManyRedirects: {e}"
    except requests.exceptions.RequestException as e:
        mention.error_message = f"Target RequestException: {e}"
    except Exception as e:
        mention.error_message = f"Target Exception: {e}"

    if mention.error_message != "":
        # There was an exception
        log.warning(f"Failed for target {mention.target_url}")
        mention.status = OutgoingWebmention.Status.TARGET_UNREACHABLE

    elif response.status_code >= 300:
        log.warning(f"{mention.target_url} returned status {response.status_code}")
        mention.status = OutgoingWebmention.Status.TARGET_ERROR
        mention.target_response_code = response.status_code

    else:
        mention.target_response_code = response.status_code

        endpoint_url = _get_absolute_endpoint_from_response(response)

        if endpoint_url:
            log.info(f"Found endpoint: {endpoint_url}")

            try:
                payload = {"target": mention.target_url, "source": mention.source_url}
                response = requests.post(endpoint_url, data=payload, timeout=10)
            except requests.exceptions.Timeout as e:
                mention.error_message = f"Endpoint Timeout: {e}"
            except requests.exceptions.TooManyRedirects as e:
                mention.error_message = f"Endpoint TooManyRedirects: {e}"
            except requests.exceptions.RequestException as e:
                mention.error_message = f"Endpoint RequestException: {e}"
            except Exception as e:
                mention.error_message = f"Endpoint Exception: {e}"

            if mention.error_message != "":
                # There was an exception
                log.warning(f"Failed for endpoint {endpoint_url}")
                mention.status = OutgoingWebmention.Status.ENDPOINT_UNREACHABLE

            elif response.status_code >= 300:
                log.warning(
                    f"Endpoint {endpoint_url} returned status {response.status_code}"
                )
                mention.status = OutgoingWebmention.Status.ENDPOINT_ERROR
                mention.endpoint_response_code = response.status_code
            else:
                log.info(
                    f"Endpoint {endpoint_url} returned status {response.status_code}"
                )
                mention.endpoint_response_code = response.status_code
                mention.status = OutgoingWebmention.Status.OK
                is_success = True
        else:
            log.info(f"No endpoint found for {mention.target_url}")
            mention.status = OutgoingWebmention.Status.NO_ENDPOINT

    mention.save()

    return is_success


def _get_absolute_endpoint_from_response(response: requests.Response) -> Optional[str]:
    endpoint = _get_endpoint_in_http_headers(response) or _get_endpoint_in_html(
        response
    )
    abs_url = _relative_to_absolute_url(response, endpoint)
    return abs_url


def _get_endpoint_in_http_headers(response: requests.Response) -> Optional[str]:
    """Search for webmention endpoint in HTTP headers."""
    try:
        header_link = response.headers.get("Link")
        if "webmention" in header_link:
            log.debug("Webmention endpoint found in http header")
            endpoint = re.match(
                r'<(?P<url>.*)>[; ]*.rel=[\'"]?webmention[\'"]?', header_link
            ).group(1)
            return endpoint
    except Exception as e:
        log.debug(f"Error reading http headers: {e}")


def _get_endpoint_in_html(response: requests.Response) -> Optional[str]:
    """Search for a webmention endpoint in HTML."""
    a_soup = BeautifulSoup(response.text, "html.parser")

    # Check HTML <head> for <link> webmention endpoint
    try:
        links = a_soup.head.find_all("link", href=True, rel=True)
        for link in links:
            if "webmention" in link["rel"]:
                endpoint = link["href"]
                log.debug("Endpoint found in document head")
                return endpoint
    except Exception as e:
        log.debug(f"Error reading <head> of external link: {e}")

    # Check HTML <body> for <a> webmention endpoint
    try:
        links = a_soup.body.find_all("a", href=True, rel=True)
        for link in links:
            if "webmention" in link["rel"]:
                log.debug("Endpoint found in document body")
                endpoint = link["href"]
                return endpoint
    except Exception as e:
        log.debug(f"Error reading <body> of link: {e}")


def _relative_to_absolute_url(response: requests.Response, url: str) -> Optional[str]:
    """
    If given url is relative, try to construct an absolute url using response domain.
    """
    if not url:
        return None

    try:
        URLValidator()(url)
        return url  # url is already well-formed.
    except ValidationError:
        scheme, domain, _, _, _ = urlsplit(response.url)
        if not scheme or not domain:
            return None
        return f"{scheme}://{domain}/" f'{url if not url.startswith("/") else url[1:]}'
