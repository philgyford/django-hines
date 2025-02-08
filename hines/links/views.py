from dal import autocomplete
from ditto.pinboard import views as pinboard_views
from ditto.pinboard.models import Bookmark, BookmarkTag
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count

from hines.core.views import PaginatedListView


class HomeView(PaginatedListView):
    template_name = "links/home.html"
    queryset = Bookmark.public_objects.all()


class BookmarkDetailView(pinboard_views.BookmarkDetailView):
    "A single Bookmark"

    template_name = "links/bookmark_detail.html"


class TagDetailView(pinboard_views.TagDetailView):
    template_name = "links/tag_detail.html"


class TagListView(pinboard_views.TagListView):
    template_name = "links/tag_list.html"


class BookmarkTagAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    """
    Used to autocomplete tag suggestions in the Admin Post change view.
    Using django-autocomplete-light.
    """

    def get_queryset(self):
        qs = BookmarkTag.objects.all()

        if self.q:
            qs = (
                qs.filter(slug__istartswith=self.q)
                .annotate(count=Count("bookmark"))
                .order_by("-count")
            )

        return qs
