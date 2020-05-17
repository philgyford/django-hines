from ditto.pinboard.models import Bookmark
from ditto.pinboard import views as pinboard_views

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
