from django.urls import path

from . import views

# Below are different url paths.
app_name = 'forum'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:thread_id>/', views.detail, name='detail'),
    path('<int:thread_id>/charts', views.pie_chart, name='pie_chart'),
    path('users', views.users, name='users'),
    path('<int:thread_id>/watch_update/', views.watch_update, name='watch_update'),
    path('watch', views.watch, name='watch')
]
