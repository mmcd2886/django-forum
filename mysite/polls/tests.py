import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Posts


class PostsModelTests(TestCase):
    def test_was_posted_recently_with_future_question(self):
        """ was_published_recently() returns False for questions whose pub_date
        is in the future. """
        time = timezone.now() + datetime.timedelta(days=30)
        future_post = Posts(date_time=time)
        self.assertIs(future_post.was_posted_recently(), False)

# to run test - 'python manage.py test polls'

