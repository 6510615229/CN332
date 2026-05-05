# a_home/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from .models import MaintenanceTask, MonthlyReport, BillingInvoice
from .forms import MaintenanceTaskForm, MonthlyReportForm, BillingProofForm

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

    maintenance_count = MaintenanceTask.objects.count()
    context = {
        'active_tab': page,
        'page_title': page_titles.get(page, page.title()),
        'maintenance_count': maintenance_count,
    }

    if page == 'dashboard':
        return dashboard_view(request, context)
    if page in ['maintenance', 'risk']:
        return maintenance_risk_report_view(request, context)
    if page == 'users':
        return user_roles_view(request, context)
    if page == 'report':
        return monthly_report_view(request, context)
    if page == 'billing':
        return billing_view(request, context)

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
    return render(request, 'juristic/maintenance_report.html', context)


@login_required
def maintenance_report_view(request, base_context=None):
    # backward compatibility if called directly
    return maintenance_risk_report_view(request, base_context)


@login_required
def dashboard_view(request, base_context=None):
    from .models import BillingInvoice, MaintenanceTask

    base_context = base_context or {}
    
    # Billing summary from database
    billing_stats = {
        'paid': BillingInvoice.objects.filter(status='paid').count(),
        'pending': BillingInvoice.objects.filter(status='pending').count(),
        'overdue': BillingInvoice.objects.filter(status='overdue').count(),
    }
    
    # Maintenance data from database
    maintenance_tasks = MaintenanceTask.objects.all().order_by('-created_at')
    maintenance_stats = {
        'total': maintenance_tasks.count(),
        'pending': maintenance_tasks.filter(status='pending').count(),
        'in_progress': maintenance_tasks.filter(status='in_progress').count(),
        'high_priority': maintenance_tasks.filter(priority='high').count(),
    }
    
    # Recent incidents (high priority tasks)
    recent_incidents = MaintenanceTask.objects.filter(priority='high').order_by('-created_at')[:3]
    
    # Maintenance schedule
    maintenance_schedule = [
        {'task': 'Fire alarm system inspection', 'time': 'Today, 2:00 PM', 'status': 'scheduled'},
        {'task': 'HVAC filter replacement', 'time': 'Tomorrow, 10:00 AM', 'status': 'scheduled'},
        {'task': 'Generator maintenance', 'time': 'Feb 10, 2026', 'status': 'scheduled'},
        {'task': 'Emergency lighting test', 'time': 'Feb 12, 2026', 'status': 'scheduled'},
    ]
    
    context = {
        **base_context,
        'billing_stats': billing_stats,
        'maintenance_stats': maintenance_stats,
        'recent_incidents': recent_incidents,
        'maintenance_schedule': maintenance_schedule,
    }
    return render(request, 'juristic/dashboard.html', context)


@login_required
def user_roles_view(request, base_context=None):
    from django.contrib.auth.models import User
    from a_users.models import Profile

    base_context = base_context or {}

    # Handle POST request for updating user role and active status
    if request.method == 'POST':
        user_id = request.POST.get('user_id')  # Get user ID from form
        role = request.POST.get('role')  # Get new role from form
        active = request.POST.get('is_active') == 'on'  # Check if user should be active
        try:
            user = User.objects.get(pk=user_id)  # Fetch the user
            
            if user.is_superuser and not active:
                active = True  # Superusers must always be active
                messages.warning(request, 'ไม่สามารถเปลี่ยนสถานะของผู้ดูแลระบบได้')
            
            else:
                profile, _ = Profile.objects.get_or_create(user=user)  # Get or create profile
                profile.role = role  # Update role
                profile.save()  # Save profile
                user.is_active = active  # Update active status
                user.save()  # Save user
                messages.success(request, 'อัปเดตข้อมูลผู้ใช้เรียบร้อยแล้ว')  # Success message
        except User.DoesNotExist:
            messages.error(request, 'ไม่พบผู้ใช้')  # Error if user not found
        return redirect('juristic_page', page='users')  # Redirect back

    # Handle GET request: fetch and display users
    users = User.objects.select_related('profile').all().order_by('-is_active', 'username')  # Get all users with profiles, ordered by active status then username

    role_choices = [('resident', 'ลูกบ้าน'), ('juristic', 'นิติบุคคล'), ('security', 'รปภ.')]  # Role options for display

    context = {
        **base_context,
        'users': users,  # Pass users to template
        'role_choices': role_choices,  # Pass role choices to template
    }
    return render(request, 'juristic/user_roles.html', context)  # Render the template


@login_required
def billing_view(request, base_context=None):
    base_context = base_context or {}
    user_role = get_user_role(request.user)

    if request.method == 'POST':
        if user_role == 'juristic' and 'update_status' in request.POST:
            invoice = get_object_or_404(BillingInvoice, pk=request.POST.get('invoice_id'))
            new_status = request.POST.get('status')
            if new_status in dict(BillingInvoice.STATUS_CHOICES):
                invoice.status = new_status
                if new_status == 'paid' and not invoice.paid_date:
                    invoice.paid_date = timezone.now().date()
                invoice.save()
                messages.success(request, 'อัปเดตสถานะใบแจ้งหนี้เรียบร้อยแล้ว')
            else:
                messages.error(request, 'สถานะไม่ถูกต้อง')
            return redirect('juristic_page', page='billing')

        if user_role == 'resident' and 'upload_proof' in request.POST:
            form = BillingProofForm(request.POST, request.FILES)
            if form.is_valid():
                invoice = get_object_or_404(
                    BillingInvoice.objects.filter(
                        Q(resident=request.user) | Q(tenant_name__iexact=request.user.profile.name),
                        pk=form.cleaned_data['invoice_id']
                    )
                )
                invoice.payment_proof = form.cleaned_data['payment_proof']
                invoice.proof_uploaded_at = timezone.now()
                invoice.proof_uploaded_by = request.user
                invoice.save()
                messages.success(request, 'อัปโหลดหลักฐานการชำระเรียบร้อยแล้ว')
            else:
                messages.error(request, 'กรุณาเลือกไฟล์ PDF ก่อนอัปโหลด')
            return redirect('resident_page', page='billing')

    if user_role == 'resident':
        invoices = BillingInvoice.objects.filter(
            Q(resident=request.user) | Q(tenant_name__iexact=request.user.profile.name)
        )
    else:
        invoices = BillingInvoice.objects.all()

    stats = {
        'total': invoices.count(),
        'paid': invoices.filter(status='paid').count(),
        'pending': invoices.filter(status='pending').count(),
        'overdue': invoices.filter(status='overdue').count(),
    }

    context = {
        **base_context,
        'invoices': invoices,
        'invoice_stats': stats,
        'status_choices': BillingInvoice.STATUS_CHOICES,
        'billing_form': BillingProofForm(),
        'user_role': user_role,
    }
    return render(request, 'juristic/billing.html', context)


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
    return render(request, 'juristic/monthly_reports.html', context)
