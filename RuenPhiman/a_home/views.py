from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User

# เรียกใช้ Model 
from .models import BillingInvoice, MonthlyReport
from a_maintenance.models import MaintenanceRequest
from .forms import MaintenanceTaskForm, MonthlyReportForm, BillingProofForm
from a_users.models import Profile
from .models import BillingInvoice

def get_user_role(user):
    try:
        return user.profile.role
    except:
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
    
    # ป้องกันการข้าม Role
    if user_role != role:
        if user_role == 'juristic':
            return redirect('a_home:juristic_page', page='dashboard')
        elif user_role == 'security':
            return redirect('a_home:security_page', page='dashboard')
        else:
            return redirect('a_home:resident_page', page='chatbot')

    # Logic สำหรับลูกบ้านส่งฟอร์มซ่อม
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

    page_titles = {
        'dashboard': 'แผงควบคุม (Dashboard)',
        'users': 'จัดการผู้ใช้งานและสิทธิ์',
        'maintenance': 'รายการแจ้งซ่อมและสถานะ',
        'billing': 'ระบบบัญชีและการเงิน',
        'report': 'รายงานประจำเดือน',
        'cctv': 'ระบบกล้องวงจรปิด',
        'incident': 'บันทึกเหตุการณ์',
        'chatbot': 'ผู้ช่วย AI Chatbot',
        'ticket': 'ติดตามสถานะงานซ่อม',
        'repair_form': 'ฟอร์มแจ้งซ่อม',
    }

    base_context = {
        'active_tab': page,
        'page_title': page_titles.get(page, page.title()),
        'user_role': user_role,
    }
    
    # Routing ไปยัง View ย่อยตาม Page
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
    
    # แก้ไขใหม่
    if user_role == 'resident' and page == 'billing':
        return billing_view(request) # <--- เอา base_context ออก

    return render(request, f'{role}/{page}.html', base_context)

@login_required
def dashboard_view(request, base_context=None):
    base_context = base_context or {}
    
    billing_stats = {
        'paid': BillingInvoice.objects.filter(status='paid').count(),
        'pending': BillingInvoice.objects.filter(status='pending').count(),
        'overdue': BillingInvoice.objects.filter(status='overdue').count(),
    }

    tasks = MaintenanceRequest.objects.all().order_by('-created_at')
    maintenance_stats = {
        'total': tasks.count(),
        'pending': tasks.filter(status='pending').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'high_priority': tasks.filter(priority='high').count(),
    }

    recent_incidents = tasks.filter(priority='high')[:3]

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
    tasks = MaintenanceRequest.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        if 'update_task' in request.POST:
            task = get_object_or_404(MaintenanceRequest, pk=request.POST.get('task_id'))
            task.status = request.POST.get('status', task.status)
            task.priority = request.POST.get('priority', task.priority)
            
            assigned_id = request.POST.get('assigned_to')
            if assigned_id:
                task.assigned_to_id = assigned_id
            
            task.save()
            messages.success(request, 'อัปเดตข้อมูลงานซ่อมสำเร็จ')
            return redirect('a_home:juristic_page', page='maintenance')

    context = {
        **base_context,
        'tasks': tasks,
        'status_choices': MaintenanceRequest.STATUS_CHOICES,
        'priority_choices': MaintenanceRequest.PRIORITY_CHOICES,
        'staff_users': User.objects.filter(is_staff=True) # สำหรับมอบหมายงาน
    }
    return render(request, 'juristic/maintenance_report.html', context)

@login_required
def user_roles_view(request, base_context=None):
    base_context = base_context or {}
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        active = request.POST.get('is_active') == 'on'
        
        user = get_object_or_404(User, pk=user_id)
        if user.is_superuser:
            messages.warning(request, 'ไม่สามารถเปลี่ยนสิทธิ์ Superuser ได้')
        else:
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = new_role
            profile.save()
            user.is_active = active
            user.save()
            messages.success(request, f'อัปเดต {user.username} สำเร็จ')
        return redirect('a_home:juristic_page', page='users')

    context = {
        **base_context,
        'users': User.objects.select_related('profile').all().order_by('-is_active'),
        'role_choices': [('resident', 'ลูกบ้าน'), ('juristic', 'นิติบุคคล'), ('security', 'รปภ.')],
    }
    return render(request, 'juristic/user_roles.html', context)

@login_required
def billing_view(request, *args, **kwargs):
    # 1. ตรวจสอบ Role (เช็กจาก URL)
    if 'juristic' in request.path:
        role = 'juristic'
    else:
        role = 'resident'

    # 2. ส่วนของ POST (จัดการส่งข้อมูล)
    if request.method == 'POST':
        # --- นิติบุคคล: ออกบิลใหม่ ---
        if 'create_invoice' in request.POST:
            unit = request.POST.get('unit')
            resident_id = request.POST.get('resident_id')
            amount = request.POST.get('amount')
            due_date = request.POST.get('due_date')
            
            resident_user = get_object_or_404(User, id=resident_id)
            
            BillingInvoice.objects.create(
                unit=unit,
                resident=resident_user,
                tenant_name=resident_user.get_full_name() or resident_user.username,
                amount=amount,
                due_date=due_date,
                status='pending'
            )
            messages.success(request, f'ออกบิลให้ห้อง {unit} เรียบร้อย!')
            return redirect(request.path)

        # --- นิติบุคคล: อัปเดตสถานะ (ปุ่ม Update) ---
        elif 'update_status' in request.POST:
            invoice_id = request.POST.get('invoice_id')
            new_status = request.POST.get('status')
            invoice = get_object_or_404(BillingInvoice, pk=invoice_id)
            invoice.status = new_status
            if new_status == 'paid':
                invoice.paid_date = timezone.now().date()
            invoice.save()
            messages.success(request, f'อัปเดตสถานะห้อง {invoice.unit} สำเร็จ')
            return redirect(request.path)

        # --- ลูกบ้าน: อัปโหลดสลิป (ปุ่ม Pay) ---
        elif 'upload_proof' in request.POST:
            invoice_id = request.POST.get('invoice_id')
            invoice = get_object_or_404(BillingInvoice, pk=invoice_id, resident=request.user)
            slip = request.FILES.get('payment_proof')
            if slip:
                invoice.payment_proof = slip
                invoice.proof_uploaded_at = timezone.now()
                invoice.status = 'pending' 
                invoice.save()
                messages.success(request, 'อัปโหลดสลิปเรียบร้อย รอตรวจสอบครับ')
            return redirect(request.path)

    #3. ส่วนของ GET (ดึงข้อมูลมาแสดงผล)
    resident_users = None
    if role == 'juristic':
        invoices = BillingInvoice.objects.all().order_by('-id')
        resident_users = User.objects.filter(is_staff=False) # ดึงรายชื่อลูกบ้านมาใส่ Dropdown
    else:
        invoices = BillingInvoice.objects.filter(resident=request.user).order_by('-id')

    # จัดเตรียมข้อมูลส่งไปที่ HTML
    context = {
        'invoices': invoices,
        'invoice_stats': {
            'total': invoices.count(),
            'paid': invoices.filter(status='paid').count(),
            'pending': invoices.filter(status='pending').count(),
            'overdue': invoices.filter(status='overdue').count(),
        },
        'user_role': role,
        'status_choices': BillingInvoice.STATUS_CHOICES,
        'active_tab': 'billing',
        'resident_users': resident_users,
        'page_title': 'ระบบบัญชีและการเงิน',
    }

    # เลือกโฟลเดอร์ไฟล์ตาม Role
    template_name = f'{role}/billing.html'
    
    return render(request, template_name, context)
    
@login_required
def monthly_report_view(request, base_context=None):
    base_context = base_context or {}
    if request.method == 'POST' and 'upload_report' in request.POST:
        form = MonthlyReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.uploaded_by = request.user
            report.save()
            messages.success(request, 'เพิ่มรายงานสำเร็จ')
            return redirect('a_home:juristic_page', page='report')
    
    context = {
        **base_context,
        'reports': MonthlyReport.objects.all().order_by('-year', '-month'),
        'report_form': MonthlyReportForm(),
    }
    return render(request, 'juristic/monthly_reports.html', context)