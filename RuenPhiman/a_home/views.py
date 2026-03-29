# a_home/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import MaintenanceTask, MonthlyReport
from .forms import MaintenanceTaskForm, MonthlyReportForm

# ฟังก์ชันตัวช่วย: จัดการกรณี User เก่าที่ role เป็นค่าว่างหรือเกิด Error
def get_user_role(user):
    try:
        role = user.profile.role
        if role:
            return role
    except:
        pass
    return 'resident'


def home_view(request):
    if request.user.is_authenticated:
        role = get_user_role(request.user)
        if role == 'juristic':
            return redirect('juristic_page', page='dashboard')
        elif role == 'security':
            return redirect('security_page', page='dashboard')
        else:
            return redirect('resident_page', page='chatbot')
    return render(request, 'home.html')


@login_required
def role_page_view(request, role, page):
    user_role = get_user_role(request.user)
    if user_role != role:
        if user_role == 'juristic':
            return redirect('juristic_page', page='dashboard')
        elif user_role == 'security':
            return redirect('security_page', page='dashboard')
        else:
            return redirect('resident_page', page='chatbot')

    page_titles = {
        'dashboard': 'Dashboard',
        'users': 'User and Roles',
        'maintenance': 'Maintenance and Risk Report',
        'billing': 'Billing',
        'report': 'Reports',
        'cctv': 'CCTV Monitoring',
        'incident': 'Incident Log',
        'chatbot': 'AI Chatbot',
        'ticket': 'Ticket Tracking',
    }

    context = {
        'active_tab': page,
        'page_title': page_titles.get(page, page.title())
    }

    if page in ['maintenance', 'risk']:
        return maintenance_risk_report_view(request, context)
    if page == 'report':
        return monthly_report_view(request, context)

    return render(request, 'role_layout.html', context)


@login_required
def maintenance_risk_report_view(request, base_context=None):
    base_context = base_context or {}

    tasks = MaintenanceTask.objects.all().order_by('-created_at')
    stats = {
        'total': tasks.count(),
        'completed': tasks.filter(status='completed').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'urgent': tasks.filter(priority='high').count(),
    }

    if request.method == 'POST':
        if 'create_task' in request.POST:
            form = MaintenanceTaskForm(request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.created_by = request.user
                task.save()
                messages.success(request, 'สร้างงานใหม่สำเร็จ')
                return redirect('juristic_page', page='maintenance')
        elif 'update_task' in request.POST:
            task = get_object_or_404(MaintenanceTask, pk=request.POST.get('task_id'))
            task.status = request.POST.get('status', task.status)
            task.priority = request.POST.get('priority', task.priority)
            task.save()
            messages.success(request, 'อัปเดตสถานะงานสำเร็จ')
            return redirect('juristic_page', page='maintenance')
    else:
        form = MaintenanceTaskForm()

    context = {
        **base_context,
        'tasks': tasks,
        'stats': stats,
        'task_form': form,
        'priority_choices': MaintenanceTask.PRIORITY_CHOICES,
        'status_choices': MaintenanceTask.STATUS_CHOICES,
    }
    return render(request, 'maintenance_report.html', context)


@login_required
def maintenance_report_view(request, base_context=None):
    # backward compatibility if called directly
    return maintenance_risk_report_view(request, base_context)

    base_context = base_context or {}

    tasks = MaintenanceTask.objects.all().order_by('-created_at')
    stats = {
        'total': tasks.count(),
        'completed': tasks.filter(status='completed').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'urgent': tasks.filter(priority='high').count(),
    }

    if request.method == 'POST':
        if 'create_task' in request.POST:
            form = MaintenanceTaskForm(request.POST)
            if form.is_valid():
                task = form.save(commit=False)
                task.created_by = request.user
                task.save()
                messages.success(request, 'สร้างงานใหม่สำเร็จ')
                return redirect('juristic_page', page='maintenance')
        elif 'update_task' in request.POST:
            task = get_object_or_404(MaintenanceTask, pk=request.POST.get('task_id'))
            task.status = request.POST.get('status', task.status)
            task.priority = request.POST.get('priority', task.priority)
            task.save()
            messages.success(request, 'อัปเดตสถานะงานสำเร็จ')
            return redirect('juristic_page', page='maintenance')
    else:
        form = MaintenanceTaskForm()

    context = {
        **base_context,
        'tasks': tasks,
        'stats': stats,
        'task_form': form,
        'priority_choices': MaintenanceTask.PRIORITY_CHOICES,
        'status_choices': MaintenanceTask.STATUS_CHOICES,
    }
    return render(request, 'maintenance_report.html', context)


# risk_management_view removed: merged into maintenance_risk_report_view


@login_required
def monthly_report_view(request, base_context=None):
    base_context = base_context or {}

    if request.method == 'POST':
        form = MonthlyReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.uploaded_by = request.user
            report.save()
            messages.success(request, 'อัปโหลดรายงานประจำเดือนเรียบร้อย')
            return redirect('juristic_page', page='report')
    else:
        form = MonthlyReportForm()

    reports = MonthlyReport.objects.order_by('-year', '-month')
    context = {
        **base_context,
        'reports': reports,
        'report_form': form,
    }
    return render(request, 'monthly_reports.html', context)
