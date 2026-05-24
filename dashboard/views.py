from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import (
    get_change_request_metrics,
    get_chart_data,
    get_quality_issue_metrics,
    get_recent_records,
)


@login_required
def home(request):
    issue_metrics = get_quality_issue_metrics()
    change_metrics = get_change_request_metrics()
    chart_data = get_chart_data()
    recent_records = get_recent_records()

    context = {
        **issue_metrics,
        **change_metrics,
        **chart_data,
        **recent_records,
    }

    return render(request, 'dashboard/home.html', context)