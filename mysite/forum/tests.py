import datetime

from django.test import TestCase
from django.utils import timezone

from .models import Threads


class ForumModelTests(TestCase):
    def test_was_created_recently_with_future_thread(self):
        """ was_created_recently() returns False for threads whose created date
        is in the future. """
        time = timezone.now() + datetime.timedelta(days=30)
        future_thread = Threads(date_time=time)
        self.assertIs(future_thread.was_created_recently(), False)

# to run test - 'python manage.py test forum'

