<<<<<<< HEAD
=======
# a_home/views.py
>>>>>>> origin/niti
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
<<<<<<< HEAD
from django.contrib.auth.models import User

from .models import MaintenanceRequest, BillingInvoice, MonthlyReport
from .forms import MaintenanceTaskForm, MonthlyReportForm, BillingProofForm
from a_users.models import Profile

=======

from .models import MaintenanceTask, MonthlyReport, BillingInvoice
from .forms import MaintenanceTaskForm, MonthlyReportForm, BillingProofForm
>>>>>>> origin/niti

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
<<<<<<< HEAD
            return redirect('a_home:resident_page', page='chatbot')

    return render(request, 'home.html') 
=======
            return redirect('resident_page', page='chatbot')
    return render(request, 'home.html')

>>>>>>> origin/niti


@login_required
def role_page_view(request, role, page):
    user_role = get_user_role(request.user)
<<<<<<< HEAD
    
=======
>>>>>>> origin/niti
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
            MaintenanceRequest.objects.create(
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
        'maintenance': 'Maintenance and Risk Report',
        'billing': 'Billing',
        'report': 'Reports',
        'cctv': 'CCTV Monitoring',
        'incident': 'Incident Log',
        'chatbot': 'AI Chatbot',
        'ticket': 'Ticket Tracking',
        'repair_form': 'Repair Form',
    }

<<<<<<< HEAD
    base_context = {
=======
    maintenance_count = MaintenanceTask.objects.count()
    context = {
>>>>>>> origin/niti
        'active_tab': page,
        'page_title': page_titles.get(page, page.title()),
        'maintenance_count': maintenance_count,
    }
<<<<<<< HEAD
    
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

    maintenance_tasks = MaintenanceRequest.objects.all().order_by('-created_at')
    maintenance_stats = {
        'total': maintenance_tasks.count(),
        'pending': maintenance_tasks.filter(status__in=['pending', 'Pending']).count(),
        'in_progress': maintenance_tasks.filter(status__in=['in_progress', 'In Progress']).count(),
        'high_priority': maintenance_tasks.filter(priority='high').count(),
    }

    recent_incidents = MaintenanceRequest.objects.filter(priority='high').order_by('-created_at')[:3]

    context = {
        **base_context,
        'billing_stats': billing_stats,
        'maintenance_stats': maintenance_stats,
        'recent_incidents': recent_incidents,
    }
    return render(request, 'juristic/dashboard.html', context)
=======

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
>>>>>>> origin/niti


@login_required
def maintenance_risk_report_view(request, base_context=None):
    base_context = base_context or {}

<<<<<<< HEAD
    tasks = MaintenanceRequest.objects.all().order_by('-created_at')
    stats = {
        'total': tasks.count(),
        'completed': tasks.filter(status__in=['completed', 'Done']).count(),
        'in_progress': tasks.filter(status__in=['in_progress', 'In Progress']).count(),
=======
    tasks = MaintenanceTask.objects.all().order_by('-created_at')
    stats = {
        'total': tasks.count(),
        'completed': tasks.filter(status='completed').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
>>>>>>> origin/niti
        'urgent': tasks.filter(priority='high').count(),
    }

    if request.method == 'POST':
        if 'create_task' in request.POST:
<<<<<<< HEAD
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
                task = get_object_or_404(MaintenanceRequest, pk=task_id)
                task.status = request.POST.get('status', task.status)
                task.priority = request.POST.get('priority', task.priority)
                
                assigned_to_id = request.POST.get('assigned_to')
                if assigned_to_id:
                    task.assigned_to_id = assigned_to_id
                    
                task.save()
                messages.success(request, 'อัปเดตสถานะเรียบร้อย')
                return redirect('a_home:juristic_page', page='maintenance')
=======
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
>>>>>>> origin/niti
    else:
        form = MaintenanceTaskForm()

    context = {
        **base_context,
        'tasks': tasks,
        'stats': stats,
        'task_form': form,
<<<<<<< HEAD
        'priority_choices': MaintenanceRequest.PRIORITY_CHOICES,
        'status_choices': MaintenanceRequest.STATUS_CHOICES,
=======
        'priority_choices': MaintenanceTask.PRIORITY_CHOICES,
        'status_choices': MaintenanceTask.STATUS_CHOICES,
>>>>>>> origin/niti
    }
    return render(request, 'juristic/maintenance_report.html', context)


@login_required
<<<<<<< HEAD
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
=======
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
>>>>>>> origin/niti


@login_required
def billing_view(request, base_context=None):
    base_context = base_context or {}
    user_role = get_user_role(request.user)

    if request.method == 'POST':
        if user_role == 'juristic' and 'update_status' in request.POST:
<<<<<<< HEAD
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
=======
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
>>>>>>> origin/niti

        if user_role == 'resident' and 'upload_proof' in request.POST:
            form = BillingProofForm(request.POST, request.FILES)
            if form.is_valid():
<<<<<<< HEAD
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
=======
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
>>>>>>> origin/niti

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


<<<<<<< HEAD
=======
# risk_management_view removed: merged into maintenance_risk_report_view


>>>>>>> origin/niti
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
<<<<<<< HEAD
            return redirect('a_home:juristic_page', page='report')
=======
            return redirect('juristic_page', page='report')
>>>>>>> origin/niti
    else:
        form = MonthlyReportForm()

    reports = MonthlyReport.objects.order_by('-year', '-month')
    context = {
        **base_context,
        'reports': reports,
        'report_form': form,
    }
    return render(request, 'juristic/monthly_reports.html', context)
