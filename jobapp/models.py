from django.db import models
import uuid

class Job(models.Model):
    job_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    device_name = models.CharField(max_length=255)
    device_ip = models.GenericIPAddressField()
    spare_name = models.CharField(max_length=255)
    spare_ip = models.GenericIPAddressField()
    status = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class JobLog(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

class Device(models.Model):
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()