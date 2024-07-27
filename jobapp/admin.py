from django.contrib import admin
from .models import Job, JobLog ,Device

class JobLogInline(admin.TabularInline):
    model = JobLog
    extra = 1

class JobAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'device_ip', 'spare_name', 'spare_ip', 'status', 'created', 'last_updated')
    search_fields = ('device_name', 'device_ip', 'spare_name', 'spare_ip', 'status')
    inlines = [JobLogInline]

class DeviceAdmin(admin.ModelAdmin):
    list_display=('name', 'ip_address')
    search_fields = ('name', 'ip_address')

admin.site.register(Job, JobAdmin)
admin.site.register(Device,DeviceAdmin)