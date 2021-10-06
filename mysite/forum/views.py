import pandas as pd
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
import nltk
from django.urls import reverse
from nltk.corpus import stopwords
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect

from .models import Posts
from .models import Threads


def index(request):
    # order threads by date_time. notice the '-' im front of 'last_date_scraped. The '-' orders it by DESC.
    threads_list = Threads.objects.order_by('-last_date_scraped')
    # get the page number from the URL
    page_number = request.GET.get('page', 1)
    # https://www.geeksforgeeks.org/how-to-add-pagination-in-django-project/
    # paginator takes list of objects as first argument and number per page as second
    paginator = Paginator(threads_list, 50)
    # will use this to prevent every page number from showing in pagination. Will only get numbers on either side of
    # current page
    # https://docs.djangoproject.com/en/3.2/ref/paginator/#django.core.paginator.Paginator.get_elided_page_range
    # https://nemecek.be/blog/105/how-to-use-elided-pagination-in-django-and-solve-too-many-pages-problem
    pagination_page_range = paginator.get_elided_page_range(number=page_number)
    try:
        thread_info = paginator.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        thread_info = paginator.page(1)
    except EmptyPage:
        # if page is empty then return last page
        thread_info = page_number.page(paginator.num_pages)
    context = {'pagination_page_range': pagination_page_range, 'threads': thread_info}
    # The render() function takes the request object as its first argument, a template name
    # as its second argument and a dictionary as its optional third argument. It returns an
    # HttpResponse object of the given template rendered with the given context.
    return render(request, 'forum/index.html', context)


def detail(request, thread_id):
    # if will run when username is submitted in form
    if request.method == 'GET' and 'fname' in request.GET:
        username_filter = request.GET.get('fname')
        replies = Posts.objects.filter(thread_id=thread_id).filter(username=username_filter).order_by('date_time')
        thread_info = Threads.objects.get(thread_id=thread_id)
        context = {'replies': replies, 'thread_info': thread_info}
        return render(request, 'forum/detail.html', context)
    else:  # get the replies from the thread
        replies_list = Posts.objects.filter(thread_id=thread_id).order_by('date_time')
    # get data for the thread so that you can display information for it in charts.html
    thread_info = Threads.objects.get(thread_id=thread_id)
    # get the page number from the URL
    page_number = request.GET.get('page', 1)
    # https://www.geeksforgeeks.org/how-to-add-pagination-in-django-project/
    # paginator takes list of objects as first argument, and number of pages for second
    paginator = Paginator(replies_list, 49)
    # will use this to prevent every page number from showing in pagination. Will only get numbers on either side of
    # current page
    # https: // docs.djangoproject.com / en / 3.2 / ref / paginator /  # django.core.paginator.Paginator.get_elided_page_range
    # https://nemecek.be/blog/105/how-to-use-elided-pagination-in-django-and-solve-too-many-pages-problem
    pagination_page_range = paginator.get_elided_page_range(number=page_number)
    try:
        replies = paginator.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        replies = paginator.page(1)
    except EmptyPage:
        # if page is empty then return the last page
        replies = page_number.page(paginator.num_pages)
    context = {'pagination_page_range': pagination_page_range, 'replies': replies, 'thread_info': thread_info}
    return render(request, 'forum/detail.html', context)


# Tutorial for visualizing using charts.js
# https://simpleisbetterthancomplex.com/tutorial/2020/01/19/how-to-use-chart-js-with-django.html
def pie_chart(request, thread_id):
    # if statement will run when a date range is submitted on the charts page. This will filter out any posts not
    # within the date range. For date_picker_end_date I hardcode seconds i.e. ':59'. This is because a user can only
    # enter hours and minutes in the range field, the seconds will default to ':00', but I want all the posts for
    # that minute so I add :59 seconds. e.g. it will search 1:15:00, but I want all replies that occurred during the
    # 15 minute mark e.g. a post at 1:15:30 will not get included.
    if request.method == 'GET' and 'start_date' in request.GET:
        date_picker_start_date = request.GET.get('start_date')
        date_picker_end_date = request.GET.get('end_date') + ':59'
        replies_from_thread_df = pd.DataFrame.from_records(Posts.objects.filter(thread_id=thread_id).filter(
            date_time__gte=date_picker_start_date, date_time__lte=date_picker_end_date).values())

    # statement will run if username is submitted in the form. Will only show charts for this username
    elif request.method == 'GET' and 'fname' in request.GET:
        username_filter = request.GET.get('fname')
        replies_from_thread_df = pd.DataFrame.from_records(
            Posts.objects.filter(thread_id=thread_id).filter(username=username_filter).values())
        # data dictionary len will be 0 if username does not exist. reload page in this case.
        if len(replies_from_thread_df) == 0:
            # raise Http404("Username Not Found")
            return redirect(request.path_info)

    # will filter out quoted replies if Include Quoted Replies box is Yes or No
    elif request.method == 'GET' and 'quote_filter' in request.GET:
        quote_filter = request.GET.get('quote_filter')
        if quote_filter == 'no':
            replies_from_thread_df = pd.DataFrame.from_records(Posts.objects.filter(thread_id=thread_id).values())
            replies_from_thread_df = replies_from_thread_df[replies_from_thread_df["quoted"] == "No quote"]
        else:
            replies_from_thread_df = pd.DataFrame.from_records(Posts.objects.filter(thread_id=thread_id).values())

    # will run when page first loads, and no form submissions have been made on the page.
    else:
        # after thread link is clicked, use thread_id to filter replies for only that thread.
        # Convert this returned sql to a dataframe
        # https://stackoverflow.com/questions/11697887/converting-django-queryset-to-pandas-dataframe
        replies_from_thread_df = pd.DataFrame.from_records(Posts.objects.filter(thread_id=thread_id).values())

    # dates for the date range picker forms
    date_of_first_reply_in_date_range = replies_from_thread_df.date_time.min()
    date_of_last_reply_in_date_range = replies_from_thread_df.date_time.max()

    # get the dates of the first and last replies posted
    df_for_getting_dates = pd.DataFrame.from_records(Posts.objects.filter(thread_id=thread_id).values())
    date_of_first_reply = df_for_getting_dates.date_time.min()
    date_of_last_reply = df_for_getting_dates.date_time.max()

    # get data for the thread so that you can display information for it in charts.html
    thread_info = Threads.objects.get(thread_id=thread_id)

    # labels to pass to charts.html for the sentiment pie chart
    sentiment_pie_chart_labels = ["Positive", "Negative", "Neutral"]

    # pie chart sentiment with quotes and with out quotes i.e. all replies
    # find the number of occurrences of Pos, Neg, Neut in sentiment column.
    quotes_sentiment_count_list = []
    quotes_df = replies_from_thread_df
    for sentiment in sentiment_pie_chart_labels:
        if sentiment in quotes_df['sentiment'].values:
            quotes_sentiment_count_list.append(quotes_df['sentiment'].value_counts()[sentiment])
        else:
            quotes_sentiment_count_list.append(0)

    # pie chart sentiment without quoted replies
    # find the number of occurrences of Pos, Neg, Neut in sentiment column.
    no_quotes_sentiment_count_list = []
    no_quotes_df = replies_from_thread_df[replies_from_thread_df["quoted"] == "No quote"]
    for sentiment in sentiment_pie_chart_labels:
        if sentiment in no_quotes_df['sentiment'].values:
            no_quotes_sentiment_count_list.append(no_quotes_df['sentiment'].value_counts()[sentiment])
        else:
            no_quotes_sentiment_count_list.append(0)

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

    # find the average sentiment score for each day
    daily_sentiment_average_df = replies_from_thread_df.set_index("date_time").groupby(pd.Grouper(freq='D'))[
        'score'].mean(). \
        reset_index(name='average score')
    daily_sentiment_average_df["date_time"] = (daily_sentiment_average_df["date_time"].dt.strftime('%Y-%m-%d'))

    # This date will be the x-axis title if there is only one day of info.
    if len(daily_sentiment_average_df["date_time"]) == 1:
        daily_sentiment_average_df = replies_from_thread_df.set_index("date_time").groupby(pd.Grouper(freq='D'))[
            'score'].mean(). \
            reset_index(name='average score')
        daily_sentiment_average_df["date_time"] = (daily_sentiment_average_df["date_time"].dt.strftime('%H:%M:%S'))
    # replace NaN with 0 otherwise chart will not display
    daily_sentiment_average_df['average score'] = daily_sentiment_average_df['average score'].fillna(0)

    daily_sentiment_average_df_line_chart_labels = daily_sentiment_average_df["date_time"].tolist()
    daily_sentiment_average_df_line_chart_data = daily_sentiment_average_df["average score"].tolist()

    # find the total pos. neg. neut. occurrences for each day. unstack() does a pivot
    daily_sentiment_total_df = replies_from_thread_df.set_index("date_time").groupby(
        pd.Grouper(freq='D')).sentiment.value_counts().to_frame().unstack(fill_value=0)
    daily_sentiment_total_df = daily_sentiment_total_df.reset_index()
    daily_sentiment_total_df["date_time"] = (daily_sentiment_total_df["date_time"].dt.strftime('%Y-%m-%d'))

    # add column name for sentiment and fill it with 0's if it does not exist
    column_name_list = [('sentiment', 'Negative'), ('sentiment', 'Neutral'), ('sentiment', 'Positive')]
    for name in column_name_list:
        if name not in daily_sentiment_total_df.columns:
            daily_sentiment_total_df[name] = 0

    total_daily_sentiment_stacked_bar_chart_labels = daily_sentiment_total_df['date_time'].tolist()
    total_daily_sentiment_stacked_bar_chart_negative_data = daily_sentiment_total_df['sentiment', 'Negative'].tolist()
    total_daily_sentiment_stacked_bar_chart_neutral_data = daily_sentiment_total_df['sentiment', 'Neutral'].tolist()
    total_daily_sentiment_stacked_bar_chart_positive_data = daily_sentiment_total_df['sentiment', 'Positive'].tolist()

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

    context = {'thread_info': thread_info,
               'sentiment_pie_chart_labels': sentiment_pie_chart_labels,
               'quotes_sentiment_count_list': quotes_sentiment_count_list,
               'sentiment_no_quotes_data': no_quotes_sentiment_count_list,
               'total_replies_datetime_bar_chart_labels': total_replies_datetime_bar_chart_labels,
               'total_replies_datetime_bar_chart_data': total_replies_datetime_bar_chart_data,
               'total_replies_by_username_labels': total_replies_by_username_labels,
               'total_replies_by_username_data': total_replies_by_username_data,
               'most_frequent_words_sorted_df_labels': most_frequent_words_sorted_df_labels,
               'most_frequent_words_sorted_df_data': most_frequent_words_sorted_df_data,
               'date_of_first_reply': date_of_first_reply,
               'date_of_last_reply': date_of_last_reply,
               'date_of_first_reply_in_date_range': date_of_first_reply_in_date_range,
               'date_of_last_reply_in_date_range': date_of_last_reply_in_date_range,
               'daily_sentiment_average_df_line_chart_labels': daily_sentiment_average_df_line_chart_labels,
               'daily_sentiment_average_df_line_chart_data': daily_sentiment_average_df_line_chart_data,
               'total_daily_sentiment_stacked_bar_chart_labels': total_daily_sentiment_stacked_bar_chart_labels,
               'total_daily_sentiment_stacked_bar_chart_negative_data': total_daily_sentiment_stacked_bar_chart_negative_data,
               'total_daily_sentiment_stacked_bar_chart_neutral_data': total_daily_sentiment_stacked_bar_chart_neutral_data,
               'total_daily_sentiment_stacked_bar_chart_positive_data': total_daily_sentiment_stacked_bar_chart_positive_data
               }
    # Pass the labels and data to charts.html so it can be visualized
    return render(request, 'forum/charts.html', context)


def users(request):
    # this is for finding all threads a user has replied to
    # when a user enters a username into the text box and submits get all posts from that user
    if request.method == 'GET':
        username_filter = request.GET.get('fname')
        posts = Posts.objects.filter(username=username_filter).order_by('date_time')
        thread_title_list = []
        thread_id_list = []
        replies_count_and_thread_title_df = pd.DataFrame()
        # get the thread_id(foreign key) from the posts and use it to get the thread title from the Threads table
        for post in posts:
            thread_id = post.thread_id
            thread_info = Threads.objects.get(thread_id=thread_id)
            thread_title_list.append(thread_info.title)
            thread_id_list.append(thread_id)
        # use a dataframe to find the total occurrences of a thread tile which will indicate how many times a
        # user replied to that thread.
        replies_count_and_thread_title_df['title'] = thread_title_list
        replies_count_and_thread_title_df['thread_id'] = thread_id_list
        grouped_df = replies_count_and_thread_title_df.groupby(['title', 'thread_id']).size().reset_index(
            name='total replies count')
        total_replies_count_list = grouped_df['total replies count'].to_list()
        thread_title_list = grouped_df['title'].to_list()
        thread_id_list = grouped_df['thread_id'].to_list()
        zipped_replies_title_list = zip(thread_title_list, total_replies_count_list, thread_id_list)

        context = {'zipped_replies_title_list': zipped_replies_title_list
                   }
        return render(request, 'forum/users.html', context)
    else:
        return render(request, 'forum/users.html')


def watch_update(request, thread_id):
    # watch-2 will be submitted from the watching page and 'watch' will be submitted from the index page
    # this will update whether a page is being watched by updating watch_list='yes' or 'no' in db
    if 'watch-2' in request.POST:
        icon_submit_yes_no = request.POST.get("watch-2")
        thread = get_object_or_404(Threads, pk=thread_id)
        thread.watch_list = icon_submit_yes_no
        thread.save()
        return HttpResponseRedirect(reverse('forum:watch'))
    else:
        if 'watch' in request.POST:
            icon_submit_yes_no = request.POST.get("watch")
            thread = get_object_or_404(Threads, pk=thread_id)
            thread.watch_list = icon_submit_yes_no
            thread.save()
            return HttpResponseRedirect(reverse('forum:index'))


def watch(request):
    # order threads by date_time. notice the '-' im front of 'last_date_scraped. The '-' orders it by DESC. Show only
    # threads with watch_list='yes'
    threads_list = Threads.objects.filter(watch_list='yes').order_by('-last_date_scraped')
    # get the page number from the URL
    page_number = request.GET.get('page', 1)
    # https://www.geeksforgeeks.org/how-to-add-pagination-in-django-project/
    # paginator takes list of objects as first argument and number per page as second
    paginator = Paginator(threads_list, 50)
    # will use this to prevent every page number from showing in pagination. Will only get numbers on either side of
    # current page
    # https://docs.djangoproject.com/en/3.2/ref/paginator/#django.core.paginator.Paginator.get_elided_page_range
    # https://nemecek.be/blog/105/how-to-use-elided-pagination-in-django-and-solve-too-many-pages-problem
    pagination_page_range = paginator.get_elided_page_range(number=page_number)

    try:
        thread_info = paginator.get_page(page_number)  # returns the desired page object
    except PageNotAnInteger:
        # if page_number is not an integer then assign the first page
        thread_info = paginator.page(1)
    except EmptyPage:
        # if page is empty then return last page
        thread_info = page_number.page(paginator.num_pages)
    context = {'pagination_page_range': pagination_page_range, 'threads': thread_info}

    # The render() function takes the request object as its first argument, a template name
    # as its second argument and a dictionary as its optional third argument. It returns an
    # HttpResponse object of the given template rendered with the given context.
    return render(request, 'forum/watch.html', context)
