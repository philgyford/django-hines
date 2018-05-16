from django.core.management.base import BaseCommand, CommandError

from hines.core.utils import datetime_now
from ...models import Post


class Command(BaseCommand):

    help = "Publishes any Posts that are scheduled with a publish time in the past."

    def handle(self, *args, **options):

        posts = Post.objects.filter(status=Post.SCHEDULED_STATUS) \
                             .filter(time_published__lte=datetime_now())

        num_posts = posts.count()

        if num_posts > 0:

            for post in posts:
                post.status = Post.LIVE_STATUS
                post.save()

            noun = 'Post' if num_posts == 1 else 'Posts'

            self.stdout.write(
                self.style.SUCCESS('{} {} published'.format(num_posts, noun))
            )
