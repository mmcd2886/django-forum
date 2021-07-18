import pandas as pd
from django.shortcuts import get_object_or_404, render

from .models import Posts
from .models import Threads


def index(request):
    latest_threads_list = Threads.objects.order_by('date_time')[:5]
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


# Tutorial for visualizing using charts.js https://simpleisbetterthancomplex.com/tutorial/2020/01/19/how-to-use-chart-js-with-django.html
def pie_chart(request, thread_id):
    # after thread link is clicked, use thread_id to filter posts for only that thread.
    # Convert this returned sql to a dataframe
    # https://stackoverflow.com/questions/11697887/converting-django-queryset-to-pandas-dataframe
    posts_from_thread_df = pd.DataFrame.from_records(Posts.objects.filter(thread_id=thread_id).values())

    # labels to pass to charts.html for the pie chart
    labels = ["Negative", "Neutral", "Positive"]

    # groupby the sentiment column (pos. neg. neut.) add up each and create the total sentiment column
    # This will be visualized in a pie chart
    sentiment_with_quotes_df = posts_from_thread_df.groupby(["sentiment"]).size().reset_index(name="total sentiment")
    print(sentiment_with_quotes_df)
    sentiment_quotes_data = sentiment_with_quotes_df["total sentiment"].tolist()
    print(sentiment_quotes_data)

    # groupby the sentiment column (pos. neg. neut.) add up each a create the total sentiment column, but do not
    # include replies that have quotes from other users in them because this could impact overall sentiment.
    # This will be visualized in a pie chart
    no_quotes_df = posts_from_thread_df[posts_from_thread_df["quoted"] == "No quote"]
    sentiment_no_quotes_df = no_quotes_df.groupby(["sentiment"]).size().reset_index(name="total sentiment")
    print(sentiment_no_quotes_df)
    sentiment_no_quotes_data = sentiment_no_quotes_df["total sentiment"].tolist()
    print(sentiment_no_quotes_data)

    # Pass the labels for the pie charts and total sentiment to charts.html so it can be visualized
    return render(request, 'polls/charts.html',  {'labels': labels, 'sentiment_quotes_data': sentiment_quotes_data,
                                                  'sentiment_no_quotes_data': sentiment_no_quotes_data})
