from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='traceroute'),
    path('getTasks', views.tasks_data, name='task-data'),
    path('runscript', views.traceroute_request, name='run-script'),
    path('traceData', views.traceroute_data,name='trace-data')
    # path('getTracerouteData', views.traceroute_data, name='traceroute-data')
]
