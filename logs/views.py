from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import OperationLog

@login_required
def log_list(request):
    if not request.user.is_super_admin:
        return render(request, '403.html', status=403)
    query = request.GET.get('q', '')
    logs = OperationLog.objects.all()
    if query:
        logs = logs.filter(object_repr__icontains=query)
    logs = logs.order_by('-created_at')
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'logs/log_list.html', {'page_obj': page_obj, 'query': query}) 