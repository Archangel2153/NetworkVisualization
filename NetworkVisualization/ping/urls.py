from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='ping'),
    path('runscript', views.ping_request, name='run-script'),
    path('getTasks', views.tasks_data, name='task-data'),
    path('getPingData', views.ping_data, name='ping-data'),
    path('getTimelineData', views.timeline_data, name='timeline-data')
]