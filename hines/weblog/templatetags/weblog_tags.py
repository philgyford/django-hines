import urllib, hashlib
from django.template import Library, Node
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.comments import Comment
from weblog.models import Entry


register = Library()

