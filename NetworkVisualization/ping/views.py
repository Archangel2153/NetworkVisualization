from django.shortcuts import render
from django.http import HttpResponseRedirect
from .pingscript import *
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .forms import PingDataForm, DomainNameForm
from background_task.models import Task, CompletedTask

def index(request):
    return render(request, 'ping.html', {})


@require_http_methods(["POST"])
def ping_request(request):
    run_ping()
    return JsonResponse({})
    #@Giblin commented
    #return HttpResponseRedirect("../pingVisualization")


def ping_to_JSON(obj):
    resp = {}
    resp['domain_name'] = obj.domain_name
    resp['ip_address'] = obj.ip_address
    resp['min_rtt'] = obj.min_rtt
    resp['avg_rtt'] = obj.avg_rtt
    resp['max_rtt'] = obj.max_rtt
    resp['rtts'] = obj.rtts
    resp['packets_sent'] = obj.packets_sent
    resp['packets_received'] = obj.packets_received
    resp['packet_loss'] = obj.packet_loss
    resp['jitter'] = obj.jitter
    resp['ping_execution'] = obj.pingExecution.starting_time
    return resp


def tasks_to_JSON(obj, done):
    resp = {}
    resp['task_name'] = obj.task_name
    resp['start'] = obj.run_at
    resp['attempts'] = obj.attempts
    resp['has_error'] = obj.has_error()
    resp['done'] = done
    return resp


@require_http_methods(["POST"])
def tasks_data(_):
    query = Task.objects.filter(task_name="ping.pingscript.run_ping")
    data = []
    for obj in query:
        data.append(tasks_to_JSON(obj,False))

    query = CompletedTask.objects.filter(task_name="ping.pingscript.run_ping")
    for obj in query:
        data.append(tasks_to_JSON(obj,True))
    return JsonResponse({"data": data})


@require_http_methods(["POST"])
def ping_data(request):
    form = PingDataForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"data": {}})

    query = PingExecution.objects.get(starting_time=form.cleaned_data['datetimefilter']).ping_set.all()

    data = []
    for obj in query:
        data.append(ping_to_JSON(obj))

    return JsonResponse({"data": data})


@require_http_methods(["POST"])
def timeline_data(request):
    form = DomainNameForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"data": {}})


    query = Ping.objects.filter(domain_name__exact=form.cleaned_data['domainnamefilter'])

    data = []
    for obj in query:
        data.append(ping_to_JSON(obj))

    return JsonResponse({"data": data})
