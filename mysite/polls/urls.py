from django.urls import path

from . import views

# Below are different url paths.
app_name = 'polls'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:thread_id>/', views.detail, name='detail'),
    path('<int:thread_id>/charts', views.pie_chart, name='pie_chart'),
    path('users', views.users, name='users')
]
