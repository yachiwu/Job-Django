# Generated by Django 5.0.7 on 2024-07-24 06:29

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('job_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('device_name', models.CharField(max_length=255)),
                ('device_ip', models.GenericIPAddressField()),
                ('spare_name', models.CharField(max_length=255)),
                ('spare_ip', models.GenericIPAddressField()),
                ('status', models.CharField(max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='JobLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='jobapp.job')),
            ],
        ),
    ]
