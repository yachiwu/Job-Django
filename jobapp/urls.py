from django.urls import path
from . import views

app_name = 'jobapp'
urlpatterns = [
    path('', views.JobListView.as_view(), name='job_list'),
    path('<uuid:job_id>/joblogs/', views.JobLogListView.as_view(), name='joblog_list'),
]
