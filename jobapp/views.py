from django.views.generic import ListView
from .models import Job, JobLog
from django.db.models import Q
from django.utils.dateparse import parse_datetime

from django.views.generic import ListView
from .models import Job
from django.db.models import Q
from django.utils.dateparse import parse_datetime

class JobListView(ListView):
    model = Job
    template_name = 'jobapp/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')

        if query:
            # 处理日期查询
            try:
                date_query = parse_datetime(query)
                if date_query:
                    queryset = queryset.filter(last_updated__date=date_query.date())
                else:
                    queryset = queryset.filter(
                        Q(device_name__icontains=query) |
                        Q(device_ip__icontains=query) |
                        Q(spare_name__icontains=query) |
                        Q(spare_ip__icontains=query) |
                        Q(last_updated__icontains=query)
                    )
            except ValueError:
                queryset = queryset.filter(
                    Q(device_name__icontains=query) |
                    Q(device_ip__icontains=query) |
                    Q(spare_name__icontains=query) |
                    Q(spare_ip__icontains=query) |
                    Q(last_updated__icontains=query)
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
        context['paginate_by'] = self.get_paginate_by(self.get_queryset())
        context['search_query'] = self.request.GET.get('q', '')
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
        context['job_id'] = self.kwargs.get('job_id')
        context['paginate_by'] = self.get_paginate_by(self.get_queryset())
        return context

    def get_paginate_by(self, queryset):
        paginate_by = self.request.GET.get('paginate_by', self.paginate_by)
        try:
            return int(paginate_by)
        except (TypeError, ValueError):
            return self.paginate_by
