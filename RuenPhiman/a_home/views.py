from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User

from .models import MaintenanceTicket, BillingInvoice, MonthlyReport
from .forms import MaintenanceTaskForm, MonthlyReportForm, BillingProofForm
from a_users.models import Profile


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
            return redirect('a_home:juristic_page', page='dashboard')
        elif role == 'security':
            return redirect('a_home:security_page', page='dashboard')
        else:
            return redirect('a_home:resident_page', page='chatbot')

    return render(request, 'home.html') 


@login_required
def role_page_view(request, role, page):
    user_role = get_user_role(request.user)
    
    if user_role != role:
        if user_role == 'juristic':
            return redirect('a_home:juristic_page', page='dashboard')
        elif user_role == 'security':
            return redirect('a_home:security_page', page='dashboard')
        else:
            return redirect('a_home:resident_page', page='chatbot')

    if request.method == 'POST' and role == 'resident' and page == 'repair_form':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        if title and description:
            MaintenanceTicket.objects.create(
                resident=request.user,
                title=title,
                description=description,
                image=image,
                status='pending'
            )
            messages.success(request, 'ส่งเรื่องแจ้งซ่อมเรียบร้อยแล้ว!')
            return redirect('a_home:resident_page', page='ticket')
        else:
            messages.error(request, 'กรุณากรอกข้อมูลให้ครบถ้วน')

    page_titles = {
        'dashboard': 'Dashboard',
        'users': 'User and Roles',
        'maintenance': 'Maintenance Report',
        'billing': 'Billing',
        'report': 'Report',
        'cctv': 'CCTV Monitoring',
        'incident': 'Incident Log',
        'chatbot': 'AI Chatbot',
        'ticket': 'Ticket Tracking',
        'repair_form': 'Repair Form',
    }

    base_context = {
        'active_tab': page,
        'page_title': page_titles.get(page, page.title())
    }
    
    if user_role == 'juristic':
        if page == 'dashboard':
            return dashboard_view(request, base_context)
        elif page in ['maintenance', 'risk']:
            return maintenance_risk_report_view(request, base_context)
        elif page == 'users':
            return user_roles_view(request, base_context)
        elif page == 'billing':
            return billing_view(request, base_context)
        elif page == 'report':
            return monthly_report_view(request, base_context)
    
    if user_role == 'resident' and page == 'billing':
        return billing_view(request, base_context)

    return render(request, f'{role}/{page}.html', base_context)


@login_required
def dashboard_view(request, base_context=None):
    base_context = base_context or {}
    
    billing_stats = {
        'paid': BillingInvoice.objects.filter(status='paid').count(),
        'pending': BillingInvoice.objects.filter(status='pending').count(),
        'overdue': BillingInvoice.objects.filter(status='overdue').count(),
    }

    maintenance_tasks = MaintenanceTicket.objects.all().order_by('-created_at')
    maintenance_stats = {
        'total': maintenance_tasks.count(),
        'pending': maintenance_tasks.filter(status__in=['pending', 'Pending']).count(),
        'in_progress': maintenance_tasks.filter(status__in=['in_progress', 'In Progress']).count(),
        'high_priority': maintenance_tasks.filter(priority='high').count(),
    }

    recent_incidents = MaintenanceTicket.objects.filter(priority='high').order_by('-created_at')[:3]

    context = {
        **base_context,
        'billing_stats': billing_stats,
        'maintenance_stats': maintenance_stats,
        'recent_incidents': recent_incidents,
    }
    return render(request, 'juristic/dashboard.html', context)


@login_required
def maintenance_risk_report_view(request, base_context=None):
    base_context = base_context or {}

    tasks = MaintenanceTicket.objects.all().order_by('-created_at')
    stats = {
        'total': tasks.count(),
        'completed': tasks.filter(status__in=['completed', 'Done']).count(),
        'in_progress': tasks.filter(status__in=['in_progress', 'In Progress']).count(),
        'urgent': tasks.filter(priority='high').count(),
    }

    if request.method == 'POST':
        if 'create_task' in request.POST:
            form = MaintenanceTaskForm(request.POST, request.FILES)
            if form.is_valid():
                task = form.save(commit=False)
                task.resident = request.user
                task.save()
                messages.success(request, 'สร้างงานแจ้งซ่อมสำเร็จ')
                return redirect('a_home:juristic_page', page='maintenance')
                
        elif 'update_task' in request.POST:
            task_id = request.POST.get('task_id')
            if task_id:
                task = get_object_or_404(MaintenanceTicket, pk=task_id)
                task.status = request.POST.get('status', task.status)
                task.priority = request.POST.get('priority', task.priority)
                
                assigned_to_id = request.POST.get('assigned_to')
                if assigned_to_id:
                    task.assigned_to_id = assigned_to_id
                    
                task.save()
                messages.success(request, 'อัปเดตสถานะเรียบร้อย')
                return redirect('a_home:juristic_page', page='maintenance')
    else:
        form = MaintenanceTaskForm()

    context = {
        **base_context,
        'tasks': tasks,
        'stats': stats,
        'task_form': form,
        'priority_choices': MaintenanceTicket.PRIORITY_CHOICES,
        'status_choices': MaintenanceTicket.STATUS_CHOICES,
    }
    return render(request, 'juristic/maintenance_report.html', context)


@login_required
def user_roles_view(request, base_context=None):
    base_context = base_context or {}

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            target_user = User.objects.get(pk=user_id)
            
            if target_user.is_superuser and not is_active:
                is_active = True
                messages.warning(request, 'ไม่สามารถปิดการใช้งาน Superuser ได้')
            else:
                profile, created = Profile.objects.get_or_create(user=target_user)
                if new_role:
                    profile.role = new_role
                    profile.save()
                
                target_user.is_active = is_active
                target_user.save()
                messages.success(request, f'อัปเดตข้อมูลผู้ใช้ {target_user.username} เรียบร้อย')
                
        except User.DoesNotExist:
            messages.error(request, 'ไม่พบผู้ใช้ที่ระบุ')
        
        return redirect('a_home:juristic_page', page='users')

    users = User.objects.select_related('profile').all().order_by('-is_active', 'username')
    
    role_choices = [
        ('resident', 'ลูกบ้าน'), 
        ('juristic', 'นิติบุคคล'), 
        ('security', 'รปภ.')
    ]

    context = {
        **base_context,
        'users': users,
        'role_choices': role_choices,
    }
    return render(request, 'juristic/user_roles.html', context)


@login_required
def billing_view(request, base_context=None):
    base_context = base_context or {}
    user_role = get_user_role(request.user)

    if request.method == 'POST':
        if user_role == 'juristic' and 'update_status' in request.POST:
            invoice_id = request.POST.get('invoice_id')
            if invoice_id:
                try:
                    invoice = BillingInvoice.objects.get(pk=invoice_id)
                    new_status = request.POST.get('status')
                    if new_status in dict(BillingInvoice.STATUS_CHOICES):
                        invoice.status = new_status
                        if new_status == 'paid' and not invoice.paid_date:
                            invoice.paid_date = timezone.now().date()
                        invoice.save()
                        messages.success(request, 'อัปเดตสถานะใบแจ้งหนี้เรียบร้อย')
                    else:
                        messages.error(request, 'สถานะไม่ถูกต้อง')
                except BillingInvoice.DoesNotExist:
                    messages.error(request, 'ไม่พบใบแจ้งหนี้')
            return redirect('a_home:juristic_page', page='billing')

        if user_role == 'resident' and 'upload_proof' in request.POST:
            form = BillingProofForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    invoice = BillingInvoice.objects.get(
                        pk=form.cleaned_data['invoice_id'],
                        resident=request.user
                    )
                    invoice.payment_proof = form.cleaned_data['payment_proof']
                    invoice.proof_uploaded_at = timezone.now()
                    invoice.proof_uploaded_by = request.user
                    invoice.save()
                    messages.success(request, 'อัปโหลดหลักฐานการชำระเงินเรียบร้อย')
                except BillingInvoice.DoesNotExist:
                    messages.error(request, 'ไม่พบใบแจ้งหนี้ของคุณ')
            else:
                messages.error(request, 'กรุณาเลือกไฟล์ให้ถูกต้อง')
            return redirect('a_home:resident_page', page='billing')

    if user_role == 'resident':
        invoices = BillingInvoice.objects.filter(
            Q(resident=request.user) | 
            Q(tenant_name__iexact=request.user.get_full_name()) |
            Q(tenant_name__iexact=request.user.username)
        ).distinct()
    else:
        invoices = BillingInvoice.objects.all().order_by('-due_date')

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
            return redirect('a_home:juristic_page', page='report')
    else:
        form = MonthlyReportForm()

    reports = MonthlyReport.objects.order_by('-year', '-month')
    context = {
        **base_context,
        'reports': reports,
        'report_form': form,
    }
    return render(request, 'juristic/monthly_reports.html', context)
