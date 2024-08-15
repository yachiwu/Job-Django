from datetime import datetime, date, time
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import ListView,DetailView
from .models import Job, JobLog, Device
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware, get_current_timezone
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pytz
from .service import fetch_location_data_from_api

class JobListView(ListView):
    model = Job
    template_name = 'jobapp/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 5

    def get_default_local_date(self):
        """Return today's date formatted for the date input field."""
        return date.today().strftime('%Y-%m-%d')

    def convert_to_utc(self, local_datetime):
        """Convert a local datetime to UTC."""
        local_timezone = get_current_timezone()
        aware_datetime = make_aware(local_datetime, timezone=local_timezone)
        return aware_datetime.astimezone(pytz.utc)

    def get_date_range(self, local_date):
        """Return the start and end of a local date as UTC."""
        start_of_day = datetime.combine(local_date, time.min)
        end_of_day = datetime.combine(local_date, time.max)
        # Convert to UTC directly
        start_of_day_utc = self.convert_to_utc(start_of_day)
        end_of_day_utc = self.convert_to_utc(end_of_day)
        return start_of_day_utc, end_of_day_utc

    # def get(self, request, *args, **kwargs):
    #     # If no last_updated parameter, redirect to include today's date
    #     if not request.GET.get('last_updated'):
    #         today_date = self.get_default_local_date()
    #         return HttpResponseRedirect(f"{request.path}?last_updated={today_date}")
    #     return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        last_updated_query = self.request.GET.get('last_updated')
        search_query = self.request.GET.get('search')

        if last_updated_query:
            try:
                last_updated_parsed = parse_date(last_updated_query)
                if last_updated_parsed:
                    start_of_day_utc, end_of_day_utc = self.get_date_range(last_updated_parsed)
                    queryset = queryset.filter(last_updated__range=(start_of_day_utc, end_of_day_utc))
            except ValueError:
                pass
        # else:
        #     today_date = date.today()
        #     start_of_today_utc, end_of_today_utc = self.get_date_range(today_date)
        #     queryset = queryset.filter(last_updated__range=(start_of_today_utc, end_of_today_utc))

        if search_query:
            queryset = queryset.filter(
                Q(device_name__icontains=search_query) |
                Q(device_ip__icontains=search_query) |
                Q(spare_name__icontains=search_query) |
                Q(spare_ip__icontains=search_query)
            )

        return queryset

    def get_paginate_by(self, queryset):
        paginate_by = self.request.GET.get('paginate_by', self.paginate_by)
        try:
            return int(paginate_by)
        except (TypeError, ValueError):
            return self.paginate_by

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        
        # Create a dictionary to store the device IDs
        switchs_id = {}
        for job in queryset:
            device = Device.objects.filter(name=job.device_name).first()
            spare_device = Device.objects.filter(name=job.spare_name).first()
            switchs_id[job.job_id] = {
                'device_id': device.id if device else None,
                'spare_device_id': spare_device.id if spare_device else None
            }
    
        context['switchs_id'] = switchs_id
        
        context['paginate_by'] = self.get_paginate_by(self.get_queryset())
        context['search_query'] = self.request.GET.get('search', '')
        # set default last_updated_query to today
        # context['last_updated_query'] = self.request.GET.get('last_updated', self.get_default_local_date())
        context['last_updated_query'] = self.request.GET.get('last_updated', '')
        context['total_count'] = queryset.count()
        return context

class JobLogListView(ListView):
    model = JobLog
    template_name = 'jobapp/joblog_list.html'
    context_object_name = 'joblogs'
    paginate_by = 5  # Default value

    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        return JobLog.objects.filter(job_id=job_id).order_by('created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(Job, job_id=job_id)

        context['job'] = job
        context['paginate_by'] = self.get_paginate_by(self.get_queryset())
        return context

    def get_paginate_by(self, queryset):
        paginate_by = self.request.GET.get('paginate_by', self.paginate_by)
        try:
            return int(paginate_by)
        except (TypeError, ValueError):
            return self.paginate_by

class DeviceDetailView(DetailView):
    model = Device
    template_name = 'jobapp/device_detail.html'
    context_object_name = 'device'
    # default is used pk , change to use id feild
    def get_object(self, queryset=None):
        return get_object_or_404(Device, id=self.kwargs.get('id'))
    
class JobStatusUpdateView(View):
    def get(self, request, *args, **kwargs):
        job_id = kwargs.get('job_id')
        job = get_object_or_404(Job, job_id=job_id)
        return render(request, 'jobapp/confirm_job_complete.html', {'job': job})
    
    def post(self, request, *args, **kwargs):
        job_id = kwargs.get('job_id')
        job = get_object_or_404(Job, job_id=job_id)
        job.status = 'complete'
        job.save()
        JobLog.objects.create(
            job=job,
            message="Job status changed to complete",
        )
        messages.success(request, f"Job ID {job.job_id} status has been changed to 'Complete'.")
        return redirect(reverse('jobs:job_list'))
    
class LocationListView(View):
    template_name = 'external/location_list.html'
    paginate_by = 20

    def get(self, request, *args, **kwargs):
        # Get the page number from the GET parameters
        page_number = request.GET.get('page', 1)
        page_number = int(page_number)
        offset = (int(page_number) - 1) * self.paginate_by

        # Build API URL with limit and offset
        api_url = f'https://demo.nautobot.com/api/dcim/locations/?depth=1&limit={self.paginate_by}&offset={offset}'
        api_token = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        
        # Fetch data from the API using the extracted function
        response_data = fetch_location_data_from_api(api_url, api_token, self.paginate_by, offset)

        # Extract data from the API response
        locations = response_data.get('results', [])
        total_count = response_data['count']
        next_page = response_data.get('next')
        previous_page = response_data.get('previous')

        # Calculate total pages
        total_pages = (total_count + self.paginate_by - 1) // self.paginate_by

        # Generate page range with ellipses
        page_range = self.get_elided_page_range(page_number, total_pages)

        context = {
            'locations': locations,
            'page_range': page_range,
            'current_page': page_number,
            'total_pages': total_pages,
            'next_page': next_page,
            'previous_page': previous_page,
        }
        return render(request, self.template_name, context)

    def get_elided_page_range(self, current_page, total_pages, num_pages=5):
        """
        Generates a page range with ellipses for pagination, retaining the current page, previous and next 2 pages,
        as well as the first and last pages.
        """
        # Calculate the range of pages to display
        start = max(1, current_page - 2)
        end = min(total_pages, current_page + 2)

        # Ensure there are enough pages before the current page
        if start > 2:
            pages = [1, '...']
            pages.extend(range(start, end + 1))
        else:
            pages = list(range(1, end + 1))
        
        # Ensure there are enough pages after the current page
        if end < total_pages - 1:
            pages.extend(['...', total_pages])
        elif end < total_pages:
            pages.append(total_pages)

        return pages
