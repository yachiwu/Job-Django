from django.contrib import admin
from .models import Job, JobLog

class JobLogInline(admin.TabularInline):
    model = JobLog
    extra = 1

class JobAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'device_ip', 'spare_name', 'spare_ip', 'status', 'created', 'last_updated')
    search_fields = ('device_name', 'device_ip', 'spare_name', 'spare_ip', 'status')
    inlines = [JobLogInline]

admin.site.register(Job, JobAdmin)
