from django.shortcuts import render
from django.http import HttpResponse
from traceroute.traceroutescript import *
from django.views.decorators.http import require_http_methods
from background_task.models import Task, CompletedTask
from .models import TracerouteExecution
from django.http import JsonResponse
import os
import binascii
from .forms import TraceDataForm

def index(request):
    return render(request, 'traceroute.html', {})

def hop_to_JSON(hop):
    if hop.longitude != 0 and hop.latitude != 0:
        return {"ll" : hop.longitude, "lt" : hop.latitude, "asn" : hop.asn, "cc" : hop.country_code}
    return None

def trace_to_JSON(trace):
    data = []
    for hop in trace:
        d = hop_to_JSON(hop)
        if d != None:         
            data.append(d)
    return data

@require_http_methods(["POST"])
def traceroute_data(request):
    form =TraceDataForm(request.POST)

    if not form.is_valid():
        return JsonResponse({"data": {}})

    cleaned_data = form.cleaned_data
    query = TracerouteExecution.objects.get(starting_time=cleaned_data['datetimefilter']).trace_set.all()
    query = list(query.filter(domain_name=cleaned_data['domainnamefilter']))[0].hop.all()

    return JsonResponse({"data": trace_to_JSON(query)})

def tasks_to_JSON(obj, done):
    resp = {}
    resp['task_name'] = obj.task_name
    resp['start'] = obj.run_at
    resp['attempts'] = obj.attempts
    resp['has_error'] = obj.has_error()
    uuid = 0
    if not done:
        uuid = obj.params()[0][0]
    progress = 0
    try:
        te = list(TracerouteExecution.objects.filter(uuid=uuid))
        progress = te[0].progress
    except:
        pass
    resp['progress'] = progress
    resp['done'] = done
    return resp

@require_http_methods(["POST"])
def tasks_data(_):
    query = Task.objects.filter(task_name="traceroute.traceroutescript.run_traceroute")
    data = []
    for obj in query:
        data.append(tasks_to_JSON(obj, False))

    query = CompletedTask.objects.filter(task_name="traceroute.traceroutescript.run_traceroute")   
    for obj in query:
        data.append(tasks_to_JSON(obj, True))
    return JsonResponse({"data": data})

def traceroute_request(request):
    uuid = binascii.hexlify(os.urandom(64)).decode()
    run_traceroute(uuid)
    return HttpResponse("test", 200)