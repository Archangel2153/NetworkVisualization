from datetime import datetime
from django.db import models
from datetime import datetime
from django.contrib import admin


class PingExecution(models.Model):
    starting_time = models.DateTimeField(default=datetime.now())


class Ping(models.Model):
    '''
    A ping defines one measurement of a website. 
    '''
    # 253 character is max official length of domain name
    domain_name = models.CharField(max_length=256, default="")
    ip_address = models.GenericIPAddressField(unpack_ipv4=True)
    min_rtt = models.FloatField(default=0)
    avg_rtt = models.FloatField(default=0)
    max_rtt = models.FloatField(default=0)
    rtts = models.CharField(max_length=256, default="")
    packets_sent = models.SmallIntegerField(default=0)
    packets_received = models.SmallIntegerField(default=0)
    packet_loss = models.FloatField(default=0)
    jitter = models.FloatField(default=0)

    pingExecution = models.ForeignKey(PingExecution, on_delete=models.CASCADE)
