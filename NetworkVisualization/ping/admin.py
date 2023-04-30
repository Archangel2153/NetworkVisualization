from django.contrib import admin
from .models import Ping, PingExecution

@admin.action(description='Remove all pings')
def remove_pings(modeladmin, request, queryset):
    Ping.objects.all().delete()

class PingAdmin(admin.ModelAdmin):
    actions = [remove_pings] 


admin.site.register(Ping, PingAdmin)
admin.site.register(PingExecution)