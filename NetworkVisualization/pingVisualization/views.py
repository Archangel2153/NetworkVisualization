from django.shortcuts import render
from ping.models import PingExecution, Ping

def index(request):
    starting_times = PingExecution.objects.values_list("starting_time", flat=True).order_by('-starting_time')
    domain_names = Ping.objects.values_list("domain_name", flat=True).distinct()

    starting_times = [x.strftime("%Y-%m-%d %H:%M:%S.%f") for x in starting_times]
    
    return render(
        request,
        'pingVisualization.html',
        {"datetimefilters" : list(starting_times),
        "domainnamefilters": list(domain_names)})
