from datetime import datetime

from ditto.flickr.models import Account as FlickrAccount
from ditto.flickr.models import Photo
from ditto.pinboard.models import Account as PinboardAccount
from ditto.pinboard.models import Bookmark
from django.utils import timezone

from hines.weblogs.models import Blog, Post


class RecentObjects:
    """
    For getting a list of the most recently posted objects across various apps.

    Use like:

        kinds = (('blog_posts', 'writing'),)
        objects = RecentObjects(kinds).get_objects(num=5)

    See __init__() for the valid `kinds`.

    The returned `objects` will be a list of dicts.
    Each dict will have these keys:

        'object': A Django object of the correct type, e.g. Post or Bookmark.
        OR
        'objects': A Queryset of all Photos posted on that day.

        'kind': e.g. 'blog_post', 'flickr_photos', 'pinboard_bookmark'.
        'time': The datetime this object was uploaded/published.
                OR the datetime at midnight for the day of the Photos QS.

    NOTE: Some types have a single item at a specific time.
          Some types have several items from a specific day.

    The objects will be in reverse chronological order.

    To add a new kind...

    1. Add to `valid_kind_types`.
    2. Add a check in `validate_kinds()`.
    3. Add a clause in `get_objects()`.
    4. Add a method, equivalent of `get_flickr_photos()`.
    5. Add tests.
    """

    # Will be the kinds passed to __init__(), assuming they're valid.
    kinds = []

    # __init__() throws an error if supplied with kind_types that aren't these.
    valid_kind_types = [
        "blog_posts",
        "flickr_photos",
        "pinboard_bookmarks",
    ]

    def __init__(self, kinds):
        """
        Adds the supplied list of kinds to self.kinds

        kinds is like:

        (
            ('blog_posts', 'writing'),            # A Blog slug
            ('flickr_photos', '35034346050@N01'), # A Flickr Account User's NSID
            ('pinboard_bookmarks', 'philgyford'), # A Pinboard Account's username
        )
        """
        self.kinds = []
        invalid_kinds = []

        for kind in kinds:
            if self.validate_kind(kind):
                self.kinds.append(kind)
            else:
                if len(kind) == 2:
                    invalid_kinds.append(f"{kind[0]}: {kind[1]}")
                else:
                    invalid_kinds.append(str(kind))

        if len(invalid_kinds) > 0:
            msg = "Invalid kind(s) supplied to __init__(): {}".format(
                ", ".join(invalid_kinds)
            )
            raise ValueError(msg)
        elif len(self.kinds) == 0:
            msg = "No valid kinds supplied to __init__()."
            raise ValueError(msg)

    def validate_kind(self, kind):
        """
        Checks a tuple like ('blog_posts', 'my-blog',).

        Returns True if the kind_type ('blog_posts') is one we accept AND the
        kind_id ('my-blog') matches the relevant item from that app.

        Returns False otherwise.
        """

        if len(kind) != 2:
            return False

        kind_type = kind[0]
        kind_id = kind[1]

        if kind_type not in self.valid_kind_types:
            return False

        if kind_type == "blog_posts":
            try:
                Blog.objects.get(slug=kind_id)
            except Blog.DoesNotExist:
                return False

        elif kind_type == "flickr_photos":
            try:
                FlickrAccount.objects.get(user__nsid=kind_id)
            except FlickrAccount.DoesNotExist:
                return False

        elif kind_type == "pinboard_bookmarks":
            try:
                PinboardAccount.objects.get(username=kind_id)
            except PinboardAccount.DoesNotExist:
                return False

        return True

    def get_objects(self, num=10):
        """
        Returns a list of the `num` most recently posted/uploaded public
        objects of the requested kinds.
        """
        objects = []

        for kind in self.kinds:
            kind_type = kind[0]
            kind_id = kind[1]

            if kind_type == "blog_posts":
                objects.extend(self.get_blog_posts(kind_id, num))

            elif kind_type == "flickr_photos":
                objects.extend(self.get_flickr_photos(kind_id, num))

            elif kind_type == "pinboard_bookmarks":
                objects.extend(self.get_pinboard_bookmarks(kind_id, num))

        sorted_objects = sorted(objects, key=lambda k: k["time"], reverse=True)

        return sorted_objects[:num]

    def get_blog_posts(self, blog_slug, num):
        """
        Returns a list of the `num` most recent Posts from the Blog with
        `blog_slug`.
        """
        objects = []

        posts = Post.public_objects.filter(blog__slug=blog_slug).order_by(
            "-time_published"
        )[:num]
        for post in posts:
            objects.append(
                {"kind": "blog_post", "object": post, "time": post.time_published}
            )

        return objects

    def get_flickr_photos(self, nsid, num):
        """
        Returns a list of the `num` most recent dates on which user `nsid` has
        posted photos, with a queryset of Photos for each one.

        NOTE: This has `objects` rather than `object` (a QuerySet of all the
        Photos from that day).
        """
        objects = []

        photo_dates = Photo.public_objects.filter(user__nsid=nsid).dates(
            "post_time", "day", order="DESC"
        )[:num]

        for photo_date in photo_dates:
            photos = Photo.public_objects.filter(
                user__nsid=nsid, post_time__date=photo_date
            ).order_by("post_time")

            # Turn photo_date into a timezone aware time at midnight:
            photo_time = datetime.combine(photo_date, datetime.min.time())
            photo_time = timezone.make_aware(
                photo_time, timezone.get_current_timezone()
            )

            objects.append(
                {"kind": "flickr_photos", "objects": photos, "time": photo_time}
            )

        return objects

    def get_pinboard_bookmarks(self, username, num):
        """
        Returns a list of the `num` most recent Bookmarks from `username`.
        """
        objects = []

        bookmarks = Bookmark.public_objects.filter(account__username=username).order_by(
            "-post_time"
        )[:num]

        for bookmark in bookmarks:
            objects.append(
                {
                    "kind": "pinboard_bookmark",
                    "object": bookmark,
                    "time": bookmark.post_time,
                }
            )

        return objects
