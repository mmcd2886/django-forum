# python3 manage.py dbshell

import datetime
from django.db import models
from django.utils import timezone


class Threads(models.Model):
    username = models.CharField(max_length=50)
    date_time = models.DateTimeField(max_length=18)
    replies = models.CharField(max_length=5000)
    url = models.CharField(max_length=200)
    title = models.CharField(max_length=1000)
    last_page_scraped = models.CharField(max_length=5000)

    def __str__(self):
        return self.username


class Posts(models.Model):
    username = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    thread = models.ForeignKey(Threads, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=6, decimal_places=4)
    quoted = models.CharField(max_length=8)
    sentiment = models.CharField(max_length=10)
    replies = models.CharField(max_length=10000)

    # you can only select one primary key in a Django model. UniqueConstraint allows you to set
    # two unique values (works like a composite key)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['username', 'date_time'], name='composite_key')]

    # This method is for a test
    def was_posted_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.date_time <= now

    def __str__(self):
        return self.username
