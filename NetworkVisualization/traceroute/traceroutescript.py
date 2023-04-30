from background_task import background
from icmplib import NameLookupError, ICMPv4Socket, ICMPv6Socket, ICMPRequest, Hop
from icmplib.utils import *
from icmplib.exceptions import *
from traceroute.models import HopModel, Trace, TracerouteExecution
from django.utils import timezone
import statistics
from tqdm import tqdm
import asyncio
import ipinfo
from aslookup import get_as_data, exceptions

async def async_traceroute(address, count=2, interval=0.05, timeout=2, first_hop=1,
        max_hops=30, id=None, source=None, family=None,
        **kwargs):

    if is_hostname(address):
        address = (await async_resolve(address, family))[0]

    if is_ipv6_address(address):
        _Socket = ICMPv6Socket
    else:
        _Socket = ICMPv4Socket

    id = id or unique_identifier()
    ttl = first_hop
    host_reached = False
    hops = []

    with (_Socket(source)) as sock:
        while not host_reached and ttl <= max_hops:
            reply = None
            packets_sent = 0
            rtts = []

            for sequence in range(count):
                request = ICMPRequest(
                    destination=address,
                    id=id,
                    sequence=sequence,
                    ttl=ttl,
                    **kwargs)

                try:
                    sock.send(request)
                    packets_sent += 1

                    reply = sock.receive(request, timeout)
                    rtt = (reply.time - request.time) * 1000
                    rtts.append(rtt)

                    reply.raise_for_status()
                    host_reached = True

                except TimeExceeded:
                   await asyncio.sleep(interval)

                except ICMPLibError:
                    break

            if reply:
                hop = Hop(
                    address=reply.source,
                    packets_sent=packets_sent,
                    rtts=rtts,
                    distance=ttl)

                hops.append(hop)

            ttl += 1

    return hops

async def async_multitraceroute(addresses, count=2, interval=0.05, timeout=2, concurrent_tasks=50, 
        max_hops=30, id=None, source=None, family=None,
        **kwargs):
        
    loop = asyncio.get_running_loop()
    tasks = []
    tasks_pending = set()

    for address in addresses:
        if len(tasks_pending) >= concurrent_tasks:
            _, tasks_pending = await asyncio.wait(
                tasks_pending,
                return_when=asyncio.FIRST_COMPLETED)

        task = loop.create_task(
                async_traceroute(
                address=address,
                count=count,
                interval=interval,
                timeout=timeout,
                source=source,
                family=family,
                id=id,
                max_hops=max_hops,
                **kwargs))

        tasks.append(task)
        tasks_pending.add(task)

    await asyncio.wait(tasks_pending)

    return [task.result() for task in tasks]
    
def multitraceroute(addresses, count=2, interval=0.05, timeout=2, concurrent_tasks=50, first_hop=1,
        max_hops=30, id=None, source=None, family=None,
        **kwargs):
    return asyncio.run(
        async_multitraceroute(
            addresses=addresses,
            count=count,
            interval=interval,
            timeout=timeout,
            concurrent_tasks=concurrent_tasks,
            first_hop=first_hop,
            max_hops=max_hops,
            source=source,
            family=family,
            id=id,
            **kwargs))

host_names = []

def load_host_names():
    global host_names
    print("Loading host names")
    with open("traceroute/alexa-top-100.txt") as file: 
        lines = file.readlines()
        for line in lines:
            host_names.append(line.strip())

def build_resolve_table():
    global host_names
    if(len(host_names) == 0):
        load_host_names()

    ip_addresses = []
    for host in host_names:
        address = "localhost"
        try:
            address = resolve(host, None)[0]
        except NameLookupError:
            print(f"Could not resolve: {host}")
        finally:
            ip_addresses.append(address)

    return ip_addresses

def is_public_ip(ip):
    ip = list(map(int, ip.strip().split('.')[:2]))
    if ip[0] == 10: return False
    if ip[0] == 127: return False
    if ip[0] == 172 and ip[1] in range(16, 32): return False
    if ip[0] == 192 and ip[1] == 168: return False
    return True

@background(queue='traceroute-queue')
def run_traceroute(uuid):
    ip_addresses = build_resolve_table()
    print("Running traceroute script")
 
    chunk_size = 2 # How many ip addresses we trace at the same time.

    now = timezone.now()
    traceExec = TracerouteExecution.objects.create(starting_time=now, progress=0, uuid=uuid)

    access_token = '9af660803ac382'
    handler = ipinfo.getHandler(access_token)

    index = 0
    for i in tqdm(range(0, len(ip_addresses), chunk_size)):
        traceExec.progress = int(i * 100 / len(ip_addresses))
        traceExec.save()
        hosts = multitraceroute(ip_addresses[i:i+chunk_size], interval=0, timeout=1)
        for host in hosts:
            trace = Trace.objects.create(
                domain_name=host_names[index],
                ip_address=ip_addresses[index],
                traceExec=traceExec
            )
            for hop in host:
                country_code = "none"
                if is_public_ip(hop.address):
                    details = handler.getDetails(hop.address)
                    country_code = details.country
                    as_data = "none"      
                    try:
                        as_lookup = get_as_data(hop.address, service='cymru')
                        as_data = as_lookup.handle           
                    except (exceptions.NoASDataError, exceptions.NonroutableAddressError):
                        pass
                    la = details.latitude
                    ll = details.longitude 
                else:
                    la = 0
                    ll = 0
                    as_data = "local"

                HopModel.objects.create(
                    trace=trace,
                    src=hop.address,
                    ttl=hop.distance,
                    avg_rtt=statistics.mean(hop.rtts),
                    latitude = la,
                    longitude=ll,
                    asn = as_data,
                    country_code=country_code
                )
                # hop.distance

            index+=1
    traceExec.progress = 100
    traceExec.save()
    print("Done with traceroute script")