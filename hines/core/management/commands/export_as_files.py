import re
import shutil
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError

from hines.weblogs.models import Blog, Post


class Command(BaseCommand):
    """
    Exports the content of all Blog posts or FlatPages to flat files.

    Suitable for using as the content of a Kirby website.
    Also downloads any images used in the posts/pages' HTML.

    NOTE: These it doesn't save complete HTML files, creating a static
    website. It's just the HTML of each post/page content.
    """

    help = "Exports weblog posts or flatpages as files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--destination",
            help="Path to folder in where files should go",
            required=True,
        )

        parser.add_argument(
            "--source",
            help="Either 'flatpges' or the ID of a Blog to export",
            required=True,
        )

    def handle(self, *args, **options):
        "Validate options, then do all the exporting if valid"
        destination = Path(options["destination"])
        if not destination.is_dir():
            msg = f"{destination} is not a valid directory"
            raise CommandError(msg)

        if options["source"] != "flatpages":
            try:
                Blog.objects.get(pk=options["source"])
            except Blog.DoesNotExist as err:
                msg = (
                    "source should be either 'flatpages' or the ID of a Blog, "
                    f"not '{options['source']}'"
                )
                raise CommandError(msg) from err

        if options["source"] == "flatpages":
            self.export_flatpages(destination=destination)
        else:
            self.export_posts(blog_id=options["source"], destination=destination)

    def export_flatpages(self, destination):
        "Exports all pages from the FlatPage app to files in folders"
        for page in FlatPage.objects.all():
            folder_path = self.create_folder_from_url(
                destination, page.get_absolute_url()
            )
            fields = {
                "Title": page.title,
                "Body": page.content,
            }
            self.write_file(folder_path, "page.txt", fields)
            self.write_images(folder_path, page.content)

    def export_posts(self, blog_id, destination):
        "Exports all Posts from the chosen Blog app to files in folders"
        index = 1
        previous_day = None

        for post in Post.objects.filter(blog=blog_id).order_by("time_published"):
            day = post.time_published.strftime("%Y-%m-%d")
            if day == previous_day:
                index += 1
            else:
                index = 1
            folder_path = self.create_folder_from_url(
                destination, post.get_absolute_url(), index
            )

            content = post.intro_html + "\n\n" + post.body_html
            fields = {
                "Title": post.title,
                "Date": post.time_published.strftime("%Y-%m-%d %H:%M:%S"),
                "Intro": post.intro_html,
                "Body": post.body_html,
                "Excerpt": post.excerpt,
                "Tags": ", ".join([t.name for t in post.get_tags()]),
                "Text": content,
            }
            self.write_file(folder_path, "post.txt", fields)
            # Do as for flatpages
            # Need to order them if within the same day
            # Do differently if it's draft/scheduled
            # If Flickr images, get full-size version?
            previous_day = day

    def create_folder_from_url(self, destination, url, index=None):
        """
        Given the URL of a page, creates a local folder for it.
        Returns a tuple of the folder path, and the filename to go in it.
        destination - the folder to start putting them in, e.g. "export"
        url - e.g. "/about/projects/my-project/"
        index - An integer index number to be prepended to the filename.

        That would return Path("export/about/projects/1_my-projects")
        """
        url = Path(url)
        url_parts = list(url.parts)
        if index is not None:
            last_folder = f"{index}_" + url_parts[-1]
        else:
            last_folder = url_parts[-1]
        folder_path = destination / Path(*url_parts[1:-1]) / last_folder
        folder_path.mkdir(parents=True, exist_ok=True)
        return folder_path

    def write_file(self, folder_path, filename, fields):
        """
        Writes a single file to a folder. Filename is same as the final folder.
        e.g. if folder_path is Path("export/about/1_projects") then a file will
        be written at "exports/about/1_projects/projects.txt"

        folder_path - A Pathlib file path to create the file in.
        fields - A dict of field names and field values, e.g.
            {"Title": "My Post", "Date": "2024-11-14", "Text": "<h1>Hello</h1>..."}
        """
        with open(Path(folder_path, filename), "w") as f:
            fields_list = []
            for key, val in fields.items():
                if key in ["Text", "Intro", "Body", "Excerpt"]:
                    fields_list.append(f"{key}:\n\n{val}")
                else:
                    fields_list.append(f"{key}: {val}")
            f.write("\n----\n".join(fields_list))

    def write_images(self, folder_path, html):
        """Downloads and saves any images used in the HTML
        Finds any <img> tags in the HTML and downloads the image in its src attribute.

        folder_path - Path to save images to
        html - The HTML to parse
        """
        domain = Site.objects.get_current().domain
        domain = f"https://{domain}" if settings.HINES_USE_HTTPS else f"http://{domain}"

        soup = BeautifulSoup(html, "html.parser")
        for img in soup.findAll("img"):
            url = img["src"]
            if not re.search(r"^https?://", url):
                url = f"{domain}{url}"

            filename = Path(url).parts[-1]
            response = requests.get(url, stream=True)
            if response.ok:
                with open(Path(folder_path, filename), "wb") as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
            else:
                self.stdout.write(
                    self.style.ERROR(f"Failed downloading {url} to go in {folder_path}")
                )
            time.sleep(0.5)
