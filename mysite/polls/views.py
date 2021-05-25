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
    #post = get_object_or_404(Posts, pk=post_id)
    post_list = Posts.objects.filter(thread_id=thread_id).order_by('date_time')
    context = {'post_list': post_list}
    return render(request, 'polls/detail.html', context)
