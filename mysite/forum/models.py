# python3 manage.py dbshell

import datetime
from django.db import models
from django.utils import timezone


# This table has an 'id' column
# This model is for the thread title and post by thread creator
class Threads(models.Model):
    thread_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    replies = models.CharField(max_length=5000)
    url = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=1000)
    last_page_scraped = models.CharField(max_length=5000)
    last_date_scraped = models.DateTimeField()  # most recent date that the thread was scraped
    total_views = models.CharField(max_length=500000000)
    reply_rate_percentage = models.CharField(max_length=100000, null=True, blank=True) # this will need to allow null values
    total_replies = models.CharField(max_length=5000000, null=True, blank=True) # this will need to allow null values
    total_distinct_usernames = models.CharField(max_length=100000, null=True, blank=True) # this will need to allow null values
    percent_distinct_replies = models.CharField(max_length=1000, null=True, blank=True) # this will need to allow null values
    watch_list = models.CharField(max_length=3)

    def __str__(self):
        return self.username


# This table has a 'id' column foreign keys to 'id' in threads table
# This models if for all the replies to a thread
class Posts(models.Model):
    username = models.CharField(max_length=50)
    date_time = models.DateTimeField()
    # Django automatically appends '_id' to the end of foreign key column names. So to access this
    # you will need to use thread_id
    # https://docs.djangoproject.com/en/dev/ref/models/fields/#database-representation
    thread = models.ForeignKey(Threads, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=6, decimal_places=4)
    quoted = models.CharField(max_length=8)
    sentiment = models.CharField(max_length=10)
    thread_page = models.CharField(max_length=10000)  # page number that the reply appears on
    replies = models.CharField(max_length=10000)

    # you can only select one primary key in a Django model. UniqueConstraint allows you to set two unique values (
    # works like a composite key). It is not possible for a user to  post at the same date_time, so this will serve as
    # a unique key so a users posts are not saved twice to the DB
    class Meta:
        constraints = [models.UniqueConstraint(fields=['username', 'date_time'], name='composite_key')]

    # This method is for a test
    def was_posted_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.date_time <= now

    def __str__(self):
        return self.username
