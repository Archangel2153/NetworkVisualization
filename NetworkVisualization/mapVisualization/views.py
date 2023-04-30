from django.shortcuts import render
from django.http import HttpResponse
from traceroute.models import TracerouteExecution, Trace

def index(request):
    starting_times = TracerouteExecution.objects.values_list("starting_time", flat=True).order_by('-starting_time')
    domain_names = Trace.objects.values_list("domain_name", flat=True).distinct()

    starting_times = [x.strftime("%Y-%m-%d %H:%M:%S.%f") for x in starting_times]
    return render(request, 'mapVisualization.html', {"datetimefilters" : list(starting_times),
        "domainnamefilters": list(domain_names)})