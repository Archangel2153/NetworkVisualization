from django.db import models
from datetime import datetime

class TracerouteExecution(models.Model):
    # 253 character is max official length of domain name
    starting_time = models.DateTimeField(default=datetime.now())
    uuid = models.CharField(max_length=256, default="")
    progress = models.PositiveSmallIntegerField(default=0)    
    

class Trace(models.Model):
    '''
    A traceroute for one host
    '''
    domain_name = models.CharField(max_length=256, default="")
    ip_address = models.GenericIPAddressField(unpack_ipv4=True)
  
    traceExec = models.ForeignKey(TracerouteExecution, on_delete=models.CASCADE)

class HopModel(models.Model):
    '''
    One hop in a trace
    '''
    trace = models.ForeignKey(Trace, on_delete=models.CASCADE, related_name='hop')
    src = models.GenericIPAddressField(unpack_ipv4=True)
    ttl = models.SmallIntegerField(default=0)
    avg_rtt = models.FloatField(default=0)
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)
    asn = models.CharField(max_length=256, default="")
    country_code = models.CharField(max_length=32, default="")




