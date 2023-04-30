from background_task import background
from icmplib import multiping, resolve, NameLookupError
from django.utils import timezone
from .models import Ping, PingExecution

host_names = []


def load_host_names():
    global host_names
    print("Loading host names")
    with open("ping/alexa-top-100.txt") as file:
        lines = file.readlines()
        for line in lines:
            host_names.append(line.strip())


def build_resolve_table():
    global host_names
    if (len(host_names) == 0):
        load_host_names()

    print("Resolving host names")
    ip_addresses = []
    unresolved_hosts = []
    for host in host_names:
        try:
            address = resolve(host, None)[0]
            ip_addresses.append(address)
        except NameLookupError:
            unresolved_hosts.append(host)
    return ip_addresses, unresolved_hosts


@background(queue='ping-queue')
def run_ping():
    ip_addresses, unresolved_hosts = build_resolve_table()
    print("Running ping script")
    hosts = multiping(ip_addresses, privileged=False)

    i = 0
    print("Adding hosts")
    now = timezone.now()

    pingExec = PingExecution.objects.create(starting_time=now)

    for host in hosts:
        result = Ping.objects.create(
            domain_name=host_names[i],
            ip_address=host.address,
            min_rtt=host.min_rtt,
            avg_rtt=host.avg_rtt,
            max_rtt=host.max_rtt,
            rtts=host.rtts,
            packets_sent=host.packets_sent,
            packets_received=host.packets_received,
            packet_loss=host.packet_loss,
            jitter=host.jitter,
            pingExecution=pingExec
        )
        i += 1
    print(f"Ignored unresolved hosts: {unresolved_hosts}")
    print("Done with ping script")
