# python3 manage.py dbshell

import datetime
from django.db import models
from django.utils import timezone


# This table has an 'id' column
class Threads(models.Model):
    # thread_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    date_time = models.DateTimeField(max_length=18)
    replies = models.CharField(max_length=5000)
    url = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=1000)
    last_page_scraped = models.CharField(max_length=5000)

    def __str__(self):
        return self.username


# This table has a 'thread_id' column foreign keys to 'id' in threads table
class Posts(models.Model):
    username = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    thread = models.ForeignKey(Threads, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=6, decimal_places=4)
    quoted = models.CharField(max_length=8)
    sentiment = models.CharField(max_length=10)
    thread_page = models.CharField(max_length=10000)
    replies = models.CharField(max_length=10000)

    # you can only select one primary key in a Django model. UniqueConstraint allows you to set
    # two unique values (works like a composite key). A user cannot post at the same date_time, so this will be unique
    class Meta:
        constraints = [models.UniqueConstraint(fields=['username', 'date_time'], name='composite_key')]

    # This method is for a test
    def was_posted_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.date_time <= now

    def __str__(self):
        return self.username
