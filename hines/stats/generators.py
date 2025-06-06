from collections import OrderedDict
from datetime import datetime, timezone

from ditto.flickr.models import Photo
from ditto.flickr.models import User as FlickrUser
from ditto.lastfm.models import Account as LastfmAccount
from ditto.lastfm.models import Scrobble
from ditto.pinboard.models import Account as PinboardAccount
from ditto.pinboard.models import Bookmark
from ditto.twitter.models import Tweet
from ditto.twitter.models import User as TwitterUser
from django.db.models import Count, F, Max, Min
from django.db.models.functions import TruncYear
from django.urls import reverse
from spectator.events.models import Event
from spectator.reading.utils import annual_reading_counts

from hines.weblogs.models import Post

# The methods in these generators should return dicts of this form:
#
# {
#   'title': 'My chart title',
#   'description: 'My optional description of the chart',
#   'data': [
#       {
#           'label': '2001',
#           'value': 37,
#           'url': '/optional/link/to/a/page/',
#       },
#       etc...
#   ]
# }


class Generator:
    """
    Parent class for all other kinds of generator.
    """

    def _queryset_to_list(
        self,
        qs,
        group_key,
        group_label,
        start_year=None,
        end_year=None,
        value_key="total",
    ):
        """
        Takes a Queryset that's of this form (or years can be integers):

            [
                {
                    'year': datetime.date(2017, 1, 1),
                    'total': 37,
                },
                {
                    'year': datetime.date(2019, 1, 1),
                    'total': 42,
                },
                # etc.
            ]

        and returns it as a list in this form:

            [
                {
                    'label': '2017',
                    'columns': {
                        'foo': {'label': 'Foo', 'value': 37},
                    }
                },
                {
                    'label': '2018',
                    'columns': {
                        'foo': {'label': 'Foo', 'value': 0},
                    }
                },
                {
                    'label': '2019',
                    'columns': {
                        'foo': {'label': 'Foo', 'value': 42},
                    }
                },
                # etc.
            ]

        Note:
            * It fills in any empty intermediate years with 0 values.
            * If start_year and/or end_year are provided (as integers), it
              will start and end at them, instead of the first/last QS items.
            * If the Queryset uses a different key to 'total', specify it
              as the 'value_key' parameter.
        """
        data = []

        # Put into a dict keyed by year:
        try:
            # Years are datetime.date's.
            counts = OrderedDict((c["year"].year, c[value_key]) for c in qs)
        except AttributeError:
            # Assume years are integers.
            counts = OrderedDict((c["year"], c[value_key]) for c in qs)

        if len(counts) == 0:
            return data

        if start_year is None:
            start_year = list(counts.items())[0][0]

        if end_year is None:
            end_year = list(counts.items())[-1][0]

        # In case there are years with no data, we go through ALL the possible
        # years and fill in empty years with 0 visits:
        for year in range(start_year, end_year + 1):
            year_data = {
                "label": str(year),
                "columns": {
                    group_key: {"label": group_label, "value": 0},
                },
            }
            if year in counts:
                year_data["columns"][group_key]["value"] = counts[year]

            data.append(year_data)

        return data


class EventsGenerator(Generator):
    """
    For things about Spectator Events.

    Can generate the data for a single kind, or for "all" kinds, suitable
    for a stacked bar chart.
    """

    def __init__(self, kind):
        """
        kind is like 'all', 'cinema', 'concert', 'gig', 'theatre', etc.
        """
        self.kind = kind

        # We want all the event charts to span the full possible years:
        dates = Event.objects.aggregate(Min("date"), Max("date"))
        try:
            self.start_year = dates["date__min"].year
        except AttributeError:
            self.start_year = None

        self.end_year = datetime.now(tz=timezone.utc).year

    def get_per_year(self):
        """
        Gets the data for either a single kind or all kinds.
        """
        if self.kind == "all":
            # The kinds we want to include, in this order:
            kinds = ["cinema", "theatre", "gig", "museum", "comedy"]

            all_data = {}
            for kind in kinds:
                # Get the data structure for each kind in turn, as if
                # we were only displaying it.
                # Then take out the data and put it in our all_data structure.
                kind_data = self._get_kind_per_year(kind)
                for year_data in kind_data:
                    label = year_data["label"]  # "2017"
                    if label not in all_data:
                        all_data[label] = {"label": label, "columns": {}}
                    all_data[label]["columns"][kind] = year_data["columns"][kind]

            data = {"data": list(all_data.values()), "title": "All Events"}
        else:
            # A chart for a single kind, like "cinema".
            data = {
                "data": self._get_kind_per_year(self.kind),
                "title": self._get_kind_title(self.kind),
            }

        return data

    def _get_kind_per_year(self, kind):
        """
        Returns the required data structure for a single kind.
        """
        qs = (
            Event.objects.filter(kind=kind)
            .annotate(year=TruncYear("date"))
            .values("year")
            .annotate(total=Count("id"))
            .order_by("year")
        )

        return self._queryset_to_list(
            qs,
            group_key=kind,
            group_label=self._get_kind_title(kind),
            start_year=self.start_year,
            end_year=self.end_year,
        )

    def _get_kind_title(self, kind):
        """
        Returns the plural title for a single kind.
        """
        kind_title = Event.get_kind_name_plural(kind)

        # Special cases:
        if kind == "comedy":
            kind_title = "Comedy gigs"
        elif kind in ["cinema", "theatre"]:
            kind_title += " visits"

        return kind_title


class FlickrGenerator(Generator):
    def __init__(self, nsid):
        "nsid is like '35034346050@N01'."
        self.nsid = nsid

    def get_photos_per_year(self):
        data = {
            "data": [],
            "title": "Flickr photos",
            "description": "Number of photos posted "
            f'<a href="https://www.flickr.com/photos/{self.nsid}/">on Flickr</a> '
            "per year.",
        }

        try:
            user = FlickrUser.objects.get(nsid=self.nsid)
        except FlickrUser.DoesNotExist:
            return data

        # Converting Photos' 'post_year' field into our required 'year':
        qs = (
            Photo.public_objects.filter(user=user)
            .annotate(year=F("post_year"))
            .values("year")
            .annotate(total=Count("id"))
            .order_by("year")
        )

        data["data"] = self._queryset_to_list(
            qs,
            group_key="flickr_photos",
            group_label="Flickr photos",
            end_year=datetime.now(tz=timezone.utc).year,
        )

        return data


class LastfmGenerator(Generator):
    def __init__(self, username):
        "username is like 'gyford'."
        self.username = username

    def get_scrobbles_per_year(self, start_year=None):
        "start_year is like 2006."

        data = {
            "data": [],
            "title": "Tracks listened to",
            "description": (
                "Number of scrobbles "
                f'<a href="https://www.last.fm/user/{self.username}">on Last.fm</a> '
                "per year."
            ),
        }

        try:
            account = LastfmAccount.objects.get(username=self.username)
        except LastfmAccount.DoesNotExist:
            return data

        # Converting Scrobbles' 'post_year' field into our required 'year':
        qs = (
            Scrobble.public_objects.filter(account=account)
            .annotate(year=F("post_year"))
            .values("year")
            .annotate(total=Count("id"))
            .order_by("year")
        )

        data["data"] = self._queryset_to_list(
            qs,
            group_key="lastfm_scrobbles",
            group_label="Tracks",
            start_year=start_year,
            end_year=datetime.now(tz=timezone.utc).year,
        )

        return data


class PinboardGenerator(Generator):
    def __init__(self, username):
        "username is like 'philgyford'."
        self.username = username

    def get_bookmarks_per_year(self):
        data = {
            "data": [],
            "title": "Links",
            "description": (
                "Number of links posted on Delicious, then on Pinboard, then only "
                '<a href="https://www.gyford.com/phil/links/">on this site</a>, '
                "per year."
            ),
        }

        try:
            account = PinboardAccount.objects.get(username=self.username)
        except PinboardAccount.DoesNotExist:
            return data

        # Converting Bookmarks' 'post_year' field into our required 'year':
        qs = (
            Bookmark.public_objects.filter(account=account)
            .annotate(year=F("post_year"))
            .values("year")
            .annotate(total=Count("id"))
            .order_by("year")
        )

        data["data"] = self._queryset_to_list(
            qs,
            group_key="pinboard_bookmarks",
            group_label="Links",
            end_year=datetime.now(tz=timezone.utc).year,
        )

        return data


class ReadingGenerator(Generator):
    """
    For things about Spectator Reading.
    """

    def __init__(self, kind):
        """
        kind is either 'book' or 'periodical'.
        """
        self.kind = kind

    def get_per_year(self):
        title = f"{self.kind}s read".capitalize()

        data = {
            "data": [],
            "title": title,
            "description": "Per year, determined by date finished.",
        }

        # counts will be like
        # [ {'year': date(2005, 1, 1), 'book': 37}, ... ]
        counts = annual_reading_counts(kind=self.kind)

        # The first years we have complete data for each kind:
        start_year = 2005 if self.kind == "periodical" else 1998

        end_year = datetime.now(tz=timezone.utc).year

        group_key = f"reading_{self.kind}"

        data["data"] = self._queryset_to_list(
            counts,
            group_key=group_key,
            group_label=title,
            start_year=start_year,
            end_year=end_year,
            value_key=self.kind,
        )

        # Go through and add in URLs to each year.
        for year in data["data"]:
            if year["columns"][group_key]["value"] > 0:
                year["columns"][group_key]["url"] = reverse(
                    "spectator:reading:reading_year_archive",
                    kwargs={"year": year["label"], "kind": f"{self.kind}s"},
                )

        return data


class StaticGenerator(Generator):
    """
    For all kinds of hard-coded data.
    """

    def _make_simple_data(
        self, totals, columns_key, label, chart_title, chart_description=None
    ):
        """
        Private method for generating the data most of the data methods return.
        Can only handle data for simple bar charts, not stacked.

        totals - A dict of year and value, like {"2001": 42, "2002": 50}
        columns_key - A unique key used to describe the data, like "amazon_spending"
        label - Label for the value used in the hover tooltip over a bar.
        chart_title - Title for the entire chart
        chart_description - Optional description to go under chart. Can contain HTML.
        """
        data = []

        # Ensure they're sorted by key (year):
        totals = dict(sorted(totals.items()))

        for year, count in totals.items():
            data.append(
                {
                    "label": year,
                    "columns": {columns_key: {"label": label, "value": count}},
                }
            )

        return_data = {
            "data": data,
            "title": chart_title,
        }

        if chart_description is not None:
            return_data["description"] = chart_description

        return return_data

    def get_amazon_spending_per_year(self):
        totals = {
            "1999": 117,
            "2000": 63,
            "2001": 62,
            "2002": 193,
            "2003": 105,
            "2004": 309,
            "2005": 379,
            "2006": 197,
            "2007": 157,
            "2008": 426,
            "2009": 397,
            "2010": 761,
            "2011": 468,
            "2012": 202,
            "2013": 116,
            "2014": 391,
            "2015": 125,
            "2016": 150,
            "2017": 47,
            "2018": 157,
            "2019": 51,
            "2020": 0,
            "2021": 0,
            "2022": 368,
            "2023": 91,
            "2024": 139,
        }

        data = self._make_simple_data(
            totals,
            columns_key="amazon_spending",
            label="Amount",
            chart_title="Amount spent on Amazon per year",
            chart_description="USD converted into GBP where applicable.",
        )

        data["number_format_prefix"] = "£"

        return data

    def get_diary_words_per_year(self):
        totals = {
            # "1996": 46696,  # Partial year
            "1997": 125643,
            "1998": 103359,
            "1999": 88432,
            "2000": 108429,
            "2001": 75226,
            "2002": 40419,
            "2003": 31648,
            "2004": 44537,
            "2005": 77280,
            "2006": 89983,
            "2007": 38911,
            "2008": 74180,
            "2009": 85464,
            "2010": 88061,
            "2011": 74305,
            "2012": 50409,
            "2013": 80000,
            "2014": 85572,
            "2015": 57049,
            "2016": 72438,
            "2017": 30978,
            "2018": 37442,
            "2019": 3873,
            "2020": 15636,
            "2021": 6428,
            "2022": 8941,
            "2023": 9159,
            "2024": 2057,
        }

        return self._make_simple_data(
            totals,
            columns_key="diary_words",
            label="Words",
            chart_title="Words written in diary",
        )

    def get_emails_received_per_year(self):
        barbicantalk = {
            "2009": 53,
            "2010": 57,
            "2011": 44,
            "2012": 34,
            "2013": 64,
            "2014": 18,
            "2015": 12,
            "2016": 1,
            "2017": 8,
            "2018": 20,
            "2019": 103,
            "2020": 21,
            "2021": 25,
            "2022": 10,
            "2023": 0,
            "2024": 2,
        }

        byliner = {
            "1999": 2,
            "2000": 35,
            "2001": 19,
            "2002": 33,
            "2003": 49,
            "2004": 58,
            "2005": 52,
            "2006": 78,
            "2007": 34,
            "2008": 40,
            "2009": 8,
            "2010": 49,
            "2011": 10,
        }

        crazywalls = {
            "2011": 7,
            "2012": 10,
            "2013": 3,
            "2014": 7,
            "2015": 8,
            "2016": 21,
            "2017": 3,
            "2018": 32,
            "2019": 2,
            "2020": 7,
            "2021": 5,
            "2022": 7,
            "2023": 1,
            "2024": 2,
        }

        guardian = {
            "2020": 2,
            "2021": 1,
            "2022": 7,
            "2023": 0,
            "2024": 1,
        }

        japanese = {
            "2006": 4,
            "2007": 5,
            "2008": 15,
            "2009": 6,
            "2010": 4,
            "2011": 3,
            "2012": 4,
            "2013": 6,
            "2014": 2,
            "2019": 1,
            "2020": 4,
            "2021": 9,
            "2022": 2,
            "2023": 3,
            "2024": 6,
        }

        oohdir = {
            "2022": 67,
            "2023": 69,
            "2024": 35,
        }

        # From Archive by year folders:
        personal = {
            "1995": 541,
            "1996": 792,
            "1997": 1889,
            "1998": 1702,
            "1999": 1446,
            "2000": 1898,
            "2001": 1723,
            "2002": 2719,
            "2003": 3060,
            "2004": 3255,
            "2005": 2415,
            "2006": 1813,
            "2007": 1919,
            "2008": 2464,
            "2009": 3079,
            "2010": 2423,
            "2011": 1968,
            "2012": 2199,
            "2013": 2000,
            "2014": 2238,
            "2015": 2130,
            "2016": 1945,
            "2017": 1806,
            "2018": 1417,
            "2019": 1480,
            "2020": 2117,
            "2021": 1744,
            "2022": 1719,
            "2023": 1911,
            "2024": 2066,
        }
        # Pepys Feedback:
        pepys = {
            "2002": 10,
            "2003": 866,
            "2004": 464,
            "2005": 554,
            "2006": 558,
            "2007": 389,
            "2008": 359,
            "2009": 253,
            "2010": 329,
            "2011": 508,
            "2012": 450,
            "2013": 266,
            "2014": 205,
            "2015": 212,
            "2016": 315,
            "2017": 251,
            "2018": 170,
            "2019": 239,
            "2020": 211,
            "2021": 219,
            "2022": 162,
            "2023": 312,
            "2024": 265,
        }

        whitstillman = {
            "2002": 31,
            "2003": 29,
            "2004": 26,
            "2005": 25,
            "2006": 58,
            "2007": 60,
            "2008": 12,
            "2009": 26,
            "2010": 35,
            "2011": 40,
            "2012": 79,
            "2013": 22,
            "2014": 20,
            "2015": 16,
            "2016": 5,
            "2017": 0,
            "2018": 3,
            "2019": 6,
            "2020": 24,
            "2021": 13,
            "2022": 0,
            "2023": 5,
            "2024": 0,
        }

        # All of the above dicts that we want to add up:
        mailboxes = [
            barbicantalk,
            byliner,
            crazywalls,
            guardian,
            japanese,
            oohdir,
            pepys,
            personal,
            whitstillman,
        ]

        # Add all the above yearly totals into a single dict of yearly totals:
        totals = {}

        for mailbox in mailboxes:
            for k, v in mailbox.items():
                if k in totals:
                    totals[k] += v
                else:
                    totals[k] = v

        return self._make_simple_data(
            totals,
            columns_key="emails",
            label="Emails",
            chart_title="Emails received",
            chart_description=(
                "Per year. Not counting: work, discussion lists, "
                "most newsletters, spam, or anything else I threw away."
            ),
        )

    def get_headaches_per_year(self):
        totals = {
            "2006": 29,
            "2007": 22,
            "2008": 18,
            "2009": 8,
            "2010": 10,
            "2011": 14,
            "2012": 12,
            "2013": 34,
            "2014": 47,
            "2015": 51,
            "2016": 59,
            "2017": 53,
            "2018": 43,
            "2019": 44,
            "2020": 46,
            "2021": 60,
            "2022": 61,
            "2023": 62,
            "2024": 73,
        }

        return self._make_simple_data(
            totals,
            columns_key="headaches",
            label="Headaches",
            chart_title="Headaches",
            chart_description=(
                "Per year. Those that require, or are defeated by, "
                "prescription medication."
            ),
        )

    def get_mastodon_posts_per_year(self):
        totals = {
            "2017": 21,
            "2018": 265,
            "2019": 291,
            "2020": 18,
            "2021": 4,
            "2022": 196,
            "2023": 474,
            "2024": 388,
        }

        return self._make_simple_data(
            totals,
            columns_key="posts",
            label="Mastodon posts",
            chart_title="Mastodon posts",
            chart_description=(
                "Number of tweets posted by "
                '<a href="https://mastodon.social/@philgyford">'
                "@philgyford@mastodon.social</a> per year"
            ),
        )

    def get_social_media_posts_per_year(self):
        "Twitter, Mastodon and Bluesky posts combined"

        # We never had a separate method for Bluesky posts, so they're here:
        bluesky_posts = {
            "2023": 11,
            "2024": 46,
        }

        # Get Twitter year:count in same format as above, from database:
        twitter_data = TwitterGenerator(screen_name="philgyford").get_tweets_per_year()
        twitter_posts = {
            d["label"]: d["columns"]["twitter_tweets"]["value"]
            for d in twitter_data["data"]
        }

        # Get Mastodon year:count in same format as above:
        mastodon_data = self.get_mastodon_posts_per_year()
        mastodon_posts = {
            d["label"]: d["columns"]["posts"]["value"] for d in mastodon_data["data"]
        }

        all_years = (
            list(mastodon_posts.keys())
            + list(bluesky_posts.keys())
            + list(twitter_posts.keys())
        )
        all_years = [int(y) for y in all_years]
        data = []
        for year in range(min(all_years), max(all_years)):
            columns = {
                "twitter": {"label": "Twitter (@philgyford)", "value": 0},
                "mastodon": {
                    "label": "Mastodon (@philgyford@mastodon.social)",
                    "value": 0,
                },
                "bluesky": {"label": "Bluesky (@phil.gyford.com)", "value": 0},
            }
            year = str(year)
            if year in twitter_posts:
                columns["twitter"]["value"] = twitter_posts[year]
            if year in mastodon_posts:
                columns["mastodon"]["value"] = mastodon_posts[year]
            if year in bluesky_posts:
                columns["bluesky"]["value"] = bluesky_posts[year]
            data.append({"label": year, "columns": columns})

        return {"data": data, "title": "Social media posts"}

    def get_steps_per_year(self):
        totals = {
            "2016": 6466,
            "2017": 6219,
            "2018": 6078,
            "2019": 7842,
            "2020": 6396,
            "2021": 7137,
            "2022": 6426,
            "2023": 6527,
            "2024": 7075,
        }

        return self._make_simple_data(
            totals,
            columns_key="steps",
            label="Steps",
            chart_title="Average steps per day",
            chart_description="As counted by my iPhone or Apple Watch.",
        )

    def get_days_worked_per_year(self):
        # Each of these three arrays should have the same keys.

        employment = {
            "2001": 174,
            "2002": 225,
            "2003": 115,
            "2004": 0,
            "2005": 0,
            "2006": 0,
            "2007": 0,
            "2008": 0,
            "2009": 0,
            "2010": 0,
            "2011": 0,
            "2012": 0,
            "2013": 167,
            "2014": 59,
            "2015": 0,
            "2016": 0,
            "2017": 37,
            "2018": 0,
            "2019": 0,
            "2020": 0,
            "2021": 0,
            "2022": 0,
            "2023": 0,
            "2024": 0,
        }

        freelance = {
            "2001": 0,
            "2002": 0,
            "2003": 81,
            "2004": 171,
            "2005": 148,
            "2006": 141,
            "2007": 85,
            "2008": 25,
            "2009": 137,
            "2010": 90,
            "2011": 148,
            "2012": 169,
            "2013": 13,
            "2014": 81,
            "2015": 170,
            "2016": 68,
            "2017": 35,
            "2018": 59,
            "2019": 126,
            "2020": 116,
            "2021": 33,
            "2022": 59,
            "2023": 29,
            "2024": 20,
        }

        acting = {
            "2001": 0,
            "2002": 0,
            "2003": 0,
            "2004": 0,
            "2005": 0,
            "2006": 14,
            "2007": 0,
            "2008": 3,
            "2009": 0,
            "2010": 0,
            "2011": 0,
            "2012": 0,
            "2013": 2,
            "2014": 0,
            "2015": 0,
            "2016": 0,
            "2017": 0,
            "2018": 2,
            "2019": 3,
            "2020": 0,
            "2021": 0,
            "2022": 0,
            "2023": 0,
            "2024": 0,
        }

        chart_data = []

        for year in employment:
            chart_data.append(
                {
                    "label": year,
                    "columns": {
                        "employment": {
                            "value": employment[year],
                            "label": "Employment",
                        },
                        "freelance": {"value": freelance[year], "label": "Freelance"},
                        "acting": {"value": acting[year], "label": "Acting"},
                    },
                }
            )

        return {
            "data": chart_data,
            "title": "Days worked per year",
            "description": (
                "Employment does not include holidays or sick days.<br>"
                "Freelance only includes days working for clients.<br>"
                "Acting includes paid or unpaid work."
            ),
        }

    def get_github_contributions_per_year(self):
        # From https://github.com/philgyford

        totals = {
            "2009": 11,
            "2010": 168,
            "2011": 97,
            "2012": 296,
            "2013": 620,
            "2014": 626,
            "2015": 1061,
            "2016": 1533,
            "2017": 1762,
            "2018": 2089,
            "2019": 2245,
            "2020": 2403,
            "2021": 1651,
            "2022": 2671,
            "2023": 1539,
            "2024": 958,
        }

        return self._make_simple_data(
            totals,
            columns_key="github_contributions",
            label="Contributions",
            chart_title="GitHub activity",
            chart_description=(
                "Contributions listed per year for "
                '<a href="https://github.com/philgyford">philgyford</a>.'
            ),
        )


class TwitterGenerator(Generator):
    def __init__(self, screen_name):
        "screen_name is like 'philgyford'."
        self.screen_name = screen_name

    def get_tweets_per_year(self):
        data = {
            "data": [],
            "title": "Tweets",
            "description": (
                "Number of tweets posted by "
                f'<a href="https://twitter.com/{self.screen_name}/">@{self.screen_name}'
                "</a> per year."
            ),
        }

        try:
            user = TwitterUser.objects.get(screen_name=self.screen_name)
        except TwitterUser.DoesNotExist:
            return data

        # Converting Tweets' 'post_year' field into our required 'year':
        qs = (
            Tweet.public_tweet_objects.filter(user=user)
            .annotate(year=F("post_year"))
            .values("year")
            .annotate(total=Count("id"))
            .order_by("year")
        )

        data["data"] = self._queryset_to_list(
            qs,
            group_key="twitter_tweets",
            group_label="Tweets",
            end_year=datetime.now(tz=timezone.utc).year,
        )

        return data

    def get_favorites_per_year(self):
        data = {
            "data": [],
            "title": "Tweets liked",
            "description": (
                "Number of tweets liked by "
                f'<a href="https://twitter.com/{self.screen_name}/">@'
                f"{self.screen_name}</a> per year."
            ),
        }

        try:
            user = TwitterUser.objects.get(screen_name=self.screen_name)
        except TwitterUser.DoesNotExist:
            return data

        # Converting Tweets' 'post_year' field into our required 'year':
        qs = (
            user.favorites.annotate(year=F("post_year"))
            .values("year")
            .annotate(total=Count("id"))
            .order_by("year")
        )

        data["data"] = self._queryset_to_list(
            qs,
            group_key="twitter_favorites",
            group_label="Favorites",
            end_year=datetime.now(tz=timezone.utc).year,
        )

        return data


class WeblogGenerator(Generator):
    def __init__(self, blog_slug):
        "slug is the slug of the Blog, like 'writing'."
        self.blog_slug = blog_slug

    def get_posts_per_year(self):
        """
        Writing blog posts per year.
        """

        data = {
            "title": "Writing posts",
            "description": 'Posts per year in <a href="{}">Writing</a>.'.format(
                reverse("weblogs:blog_detail", kwargs={"blog_slug": self.blog_slug})
            ),
            "data": [],
        }

        qs = (
            Post.public_objects.filter(blog__slug=self.blog_slug)
            .annotate(year=TruncYear("time_published"))
            .values("year")
            .annotate(total=Count("id"))
            .order_by("year")
        )

        data["data"] = self._queryset_to_list(
            qs,
            group_key="weblog_posts",
            group_label="Posts",
            end_year=datetime.now(tz=timezone.utc).year,
        )

        # Go through and add URLs for each year of writing.
        for year in data["data"]:
            if year["columns"]["weblog_posts"]["value"] > 0:
                year["columns"]["weblog_posts"]["url"] = reverse(
                    "weblogs:post_year_archive",
                    kwargs={"blog_slug": self.blog_slug, "year": year["label"]},
                )

        return data
