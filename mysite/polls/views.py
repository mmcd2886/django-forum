import pandas as pd
from django.shortcuts import get_object_or_404, render

from .models import Posts
from .models import Threads


def index(request):
    latest_threads_list = Threads.objects.order_by('date_time')[:20]
    context = {'latest_threads_list': latest_threads_list}
    # The render() function takes the request object as its first argument, a template name
    # as its second argument and a dictionary as its optional third argument. It returns an
    # HttpResponse object of the given template rendered with the given context.
    return render(request, 'polls/index.html', context)


def detail(request, thread_id):
    # post = get_object_or_404(Posts, pk=post_id)
    post_list = Posts.objects.filter(thread_id=thread_id).order_by('date_time')
    context = {'post_list': post_list}
    return render(request, 'polls/detail.html', context)


# Tutorial for visualizing using charts.js
# https://simpleisbetterthancomplex.com/tutorial/2020/01/19/how-to-use-chart-js-with-django.html
def pie_chart(request, thread_id):
    # after thread link is clicked, use thread_id to filter posts for only that thread.
    # Convert this returned sql to a dataframe
    # https://stackoverflow.com/questions/11697887/converting-django-queryset-to-pandas-dataframe
    posts_from_thread_df = pd.DataFrame.from_records(Posts.objects.filter(thread_id=thread_id).values())

    # labels to pass to charts.html for the pie chart
    sentiment_pie_chart_labels = ["Negative", "Neutral", "Positive"]

    # pie chart sentiment with quotes
    # groupby the sentiment column (pos. neg. neut.) add up each and create the total sentiment column
    # This will be visualized in a pie chart
    sentiment_with_quotes_df = posts_from_thread_df.groupby(["sentiment"]).size().reset_index(name="total sentiment")
    sentiment_quotes_data = sentiment_with_quotes_df["total sentiment"].tolist()

    # pie chart sentiment without quotes
    # groupby the sentiment column (pos. neg. neut.) add up each a create the total sentiment column, but do not
    # include replies that have quotes from other users in them because this could impact overall sentiment.
    # This will be visualized in a pie chart
    no_quotes_df = posts_from_thread_df[posts_from_thread_df["quoted"] == "No quote"]
    sentiment_no_quotes_df = no_quotes_df.groupby(["sentiment"]).size().reset_index(name="total sentiment")
    sentiment_no_quotes_data = sentiment_no_quotes_df["total sentiment"].tolist()

    # Total Replies on a date in Chron order bar chart
    # Groupby Day using freq='D' and then find the size() and add it to the column Total Replies which will tally
    # the total replies for each day. Convert the .size() series that it returns to a dataframe using .reset_index.
    # Convert DateTime object to just date using strftime. groupby day and show daily Total Replies.if there is only
    # one date worth of replies, use the if statement to group by hours instead to display hourly data for the single
    # day. Else groupby day and show daily Total Replies.
    total_posts_datetime_df = posts_from_thread_df.set_index("date_time").groupby(pd.Grouper(freq='D')).size(). \
        reset_index(name='total replies')
    total_posts_datetime_df["date_time"] = (total_posts_datetime_df["date_time"].dt.strftime('%Y-%m-%d'))
    # This date will be the x-axis title if there is only one day of Replies
    if len(total_posts_datetime_df["date_time"]) == 1:
        total_posts_datetime_df = posts_from_thread_df.set_index("date_time").groupby(
            pd.Grouper(freq='H')).size().reset_index(name='total replies')
        total_posts_datetime_df["date_time"] = (total_posts_datetime_df["date_time"].dt.strftime('%H:%M:%S'))

    total_posts_datetime_bar_chart_labels = total_posts_datetime_df["date_time"].tolist()
    total_posts_datetime_bar_chart_data = total_posts_datetime_df["total replies"].tolist()

    # Total Replies by a user bar chart
    # Use groupby to group by Username, then use .size() to return a series that will show the total number for each
    # username. Convert this to a dataframe using .reset_index()
    total_replies_by_username_df = posts_from_thread_df.groupby(["username"]).size().reset_index(name='total replies')
    # Sort the dataframe users most replies to least. Get the top 15 users with most replies
    total_replies_by_username_df.sort_values(by=['total replies'], inplace=True, ascending=False)
    total_replies_by_username_df = total_replies_by_username_df.head(15)

    total_replies_by_username_labels = total_replies_by_username_df['username'].tolist()
    total_replies_by_username_data = total_replies_by_username_df['total replies'].tolist()
    print(total_replies_by_username_df)

    # Pass the labels and data to charts.html so it can be visualized
    return render(request, 'polls/charts.html', {'sentiment_pie_chart_labels': sentiment_pie_chart_labels, 'sentiment_quotes_data': sentiment_quotes_data,
                                                 'sentiment_no_quotes_data': sentiment_no_quotes_data,
                                                 'total_posts_datetime_bar_chart_labels': total_posts_datetime_bar_chart_labels,
                                                 'total_posts_datetime_bar_chart_data': total_posts_datetime_bar_chart_data,
                                                 'total_replies_by_username_labels': total_replies_by_username_labels,
                                                 'total_replies_by_username_data': total_replies_by_username_data
                                                 })
