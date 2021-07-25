import pandas as pd
from django.shortcuts import get_object_or_404, render
import nltk
from nltk.corpus import stopwords

from .models import Posts
from .models import Threads


def index(request):
    latest_threads_list = Threads.objects.order_by('date_time')[:100]
    context = {'latest_threads_list': latest_threads_list}
    # The render() function takes the request object as its first argument, a template name
    # as its second argument and a dictionary as its optional third argument. It returns an
    # HttpResponse object of the given template rendered with the given context.
    return render(request, 'polls/index.html', context)


def detail(request, thread_id):
    # post = get_object_or_404(Posts, pk=post_id)
    # get data for the thread so that you can display information for it in charts.html
    thread_info = Threads.objects.get(thread_id=thread_id)
    # get the replies from the thread
    post_list = Posts.objects.filter(thread_id=thread_id).order_by('date_time')
    context = {'post_list': post_list, 'thread_info': thread_info}
    return render(request, 'polls/detail.html', context)


# Tutorial for visualizing using charts.js
# https://simpleisbetterthancomplex.com/tutorial/2020/01/19/how-to-use-chart-js-with-django.html
def pie_chart(request, thread_id):
    # get data for the thread so that you can display information for it in charts.html
    thread_info = Threads.objects.get(thread_id=thread_id)
    # after thread link is clicked, use thread_id to filter replies for only that thread.
    # Convert this returned sql to a dataframe
    # https://stackoverflow.com/questions/11697887/converting-django-queryset-to-pandas-dataframe
    replies_from_thread_df = pd.DataFrame.from_records(Posts.objects.filter(thread_id=thread_id).values())

    # labels to pass to charts.html for the sentiment pie chart
    sentiment_pie_chart_labels = ["Negative", "Neutral", "Positive"]

    # pie chart sentiment with quotes
    # groupby the sentiment column (pos. neg. neut.) add up each and create the total sentiment column
    sentiment_with_quotes_df = replies_from_thread_df.groupby(["sentiment"]).size().reset_index(name="total sentiment")
    sentiment_with_quotes_data = sentiment_with_quotes_df["total sentiment"].tolist()

    # pie chart sentiment without quotes
    # groupby the sentiment column (pos. neg. neut.) add up each a create the total sentiment column, but do not
    # include replies that have quotes from other users because this could impact overall sentiment.
    no_quotes_df = replies_from_thread_df[replies_from_thread_df["quoted"] == "No quote"]
    sentiment_no_quotes_df = no_quotes_df.groupby(["sentiment"]).size().reset_index(name="total sentiment")
    sentiment_no_quotes_data = sentiment_no_quotes_df["total sentiment"].tolist()

    # Total Replies on a day in Chron order bar chart
    # Groupby Day using freq='D' and then find the size() and add it to the column Total Replies which will tally
    # the total replies for each day. Convert the .size() series that it returns to a dataframe using .reset_index.
    # Convert DateTime object to just date using strftime. groupby day and show daily Total Replies. if there is only
    # one date worth of replies, use the if statement to group by hours instead to display hourly data for the single
    # day.
    total_replies_datetime_df = replies_from_thread_df.set_index("date_time").groupby(pd.Grouper(freq='D')).size(). \
        reset_index(name='total replies')
    total_replies_datetime_df["date_time"] = (total_replies_datetime_df["date_time"].dt.strftime('%Y-%m-%d'))
    # This date will be the x-axis title if there is only one day of Replies
    if len(total_replies_datetime_df["date_time"]) == 1:
        total_replies_datetime_df = replies_from_thread_df.set_index("date_time").groupby(
            pd.Grouper(freq='H')).size().reset_index(name='total replies')
        total_replies_datetime_df["date_time"] = (total_replies_datetime_df["date_time"].dt.strftime('%H:%M:%S'))

    total_replies_datetime_bar_chart_labels = total_replies_datetime_df["date_time"].tolist()
    total_replies_datetime_bar_chart_data = total_replies_datetime_df["total replies"].tolist()

    # Total Replies by top replying users bar chart
    # Use groupby to group by Username, then use .size() to return a series that will show the total number for each
    # username. Convert this to a dataframe using .reset_index()
    total_replies_by_username_df = replies_from_thread_df.groupby(["username"]).size().reset_index(name='total replies')
    # Sort the dataframe users most replies to least. Get the top 15 users with most replies
    total_replies_by_username_sorted_df = total_replies_by_username_df.sort_values(by=['total replies'],
                                                                                   ascending=False).head(15)

    total_replies_by_username_labels = total_replies_by_username_sorted_df['username'].tolist()
    total_replies_by_username_data = total_replies_by_username_sorted_df['total replies'].tolist()

    # Most frequent words bar chart
    # make everything lower case then tokenize
    lower_case_replies_info_df = replies_from_thread_df['replies'].str.lower().str.cat(sep=' ')
    tokenized_replies_list = nltk.tokenize.word_tokenize(lower_case_replies_info_df)

    # remove stop words
    stop_words = set(stopwords.words('english'))
    replies_with_no_stop_words_list = []
    for word in tokenized_replies_list:
        if word not in stop_words:
            replies_with_no_stop_words_list.append(word)

    # remove punctuation
    cleaned_text_list = []
    for word in replies_with_no_stop_words_list:
        if word.isalpha():
            cleaned_text_list.append(word)
    word_dist = nltk.FreqDist(cleaned_text_list)

    # number of top words to display in matplot
    most_frequent_words = 20
    most_frequent_words_df = pd.DataFrame(word_dist.most_common(most_frequent_words), columns=['Word', 'Frequency'])

    # sort from least to greatest otherwise barchart will be upside down
    most_frequent_words_sorted_df = most_frequent_words_df.sort_values(by=['Frequency'], ascending=False)
    most_frequent_words_sorted_df_labels = most_frequent_words_sorted_df['Word'].tolist()
    most_frequent_words_sorted_df_data = most_frequent_words_sorted_df['Frequency'].tolist()

    context = {'thread_info': thread_info, 'sentiment_pie_chart_labels': sentiment_pie_chart_labels,
               'sentiment_with_quotes_data': sentiment_with_quotes_data,
               'sentiment_no_quotes_data': sentiment_no_quotes_data,
               'total_replies_datetime_bar_chart_labels': total_replies_datetime_bar_chart_labels,
               'total_replies_datetime_bar_chart_data': total_replies_datetime_bar_chart_data,
               'total_replies_by_username_labels': total_replies_by_username_labels,
               'total_replies_by_username_data': total_replies_by_username_data,
               'most_frequent_words_sorted_df_labels': most_frequent_words_sorted_df_labels,
               'most_frequent_words_sorted_df_data': most_frequent_words_sorted_df_data
               }
    # Pass the labels and data to charts.html so it can be visualized
    return render(request, 'polls/charts.html', context)
