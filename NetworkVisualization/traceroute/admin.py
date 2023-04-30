from django.contrib import admin
from .models import TracerouteExecution, Trace, HopModel


admin.site.register(TracerouteExecution)
admin.site.register(Trace)
admin.site.register(HopModel)
