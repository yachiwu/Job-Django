from django.urls import path
from . import views

app_name = 'jobapp'
urlpatterns = [
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('job/<uuid:job_id>/complete/', views.JobStatusUpdateView.as_view(), name='job_complete'),
    path('confirm_job_complete/<uuid:job_id>/', views.JobStatusUpdateView.as_view(), name='confirm_job_complete'),
    path('<uuid:job_id>/joblogs/', views.JobLogListView.as_view(), name='joblog_list'),
    path('device/<int:id>/', views.DeviceDetailView.as_view(), name='device_detail'),
    path('locations/', views.LocationListView.as_view(), name='location_list'),
]

