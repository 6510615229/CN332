from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings
import json

# เรียกใช้ Model และ Form จากภายในแอป a_home ทั้งหมด
# แก้ไข: ดึง MaintenanceRequest จาก .models แทน a_maintenance.models
from .models import BillingInvoice, MonthlyReport, Notification, MaintenanceRequest, Camera, Incident
from .forms import MaintenanceTaskForm, MonthlyReportForm, BillingProofForm, IncidentForm
from .mock_cctv import MOCK_CAMERAS
from a_users.models import Profile

# --- Helper Functions ---
def get_user_role(user):
    try:
        return user.profile.role
    except:
        return 'resident'

# --- Main Views ---
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
            
            # ค้นหา User ที่มี Role เป็น 'juristic'
            juristic_users = User.objects.filter(profile__role='juristic', is_active=True)
            
            for juristic in juristic_users:
                Notification.objects.create(
                    user=juristic, # ส่งกระดิ่งไปให้นิติ
                    title="🛠️ มีคำร้องแจ้งซ่อมใหม่",
                    message=f"ห้องของ {request.user.username} แจ้งปัญหา: {title}"
                )
            # =========================================================
            
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
    
    if role == 'resident' and page == 'ticket':
        base_context['requests'] = MaintenanceRequest.objects.filter(resident=request.user).order_by('-created_at')

    # Routing
    if user_role == 'juristic':
        if page == 'dashboard': return dashboard_view(request, base_context)
        elif page in ['maintenance', 'risk']: return maintenance_risk_report_view(request, base_context)
        elif page == 'users': return user_roles_view(request, base_context)
        elif page == 'billing': return billing_view(request, base_context)
        elif page == 'report': return monthly_report_view(request, base_context)
    
    if user_role == 'resident' and page == 'billing':
        return billing_view(request, base_context=base_context)

    if user_role == 'security':
        if page == 'dashboard': return security_dashboard_view(request, base_context)
        elif page == 'cctv': return security_cctv_view(request, base_context)
        elif page == 'incident': return security_incident_view(request, base_context)

    response = render(request, f'{role}/{page}.html', base_context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# --- New Function: Mark Notification as Read ---
@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

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
    context = {**base_context, 'billing_stats': billing_stats, 'maintenance_stats': maintenance_stats, 'recent_incidents': recent_incidents}
    return render(request, 'juristic/dashboard.html', context)


@login_required
def security_dashboard_view(request, base_context=None):
    base_context = base_context or {}
    cameras = list(Camera.objects.all())
    if not cameras:
        cameras = MOCK_CAMERAS
    if cameras and isinstance(cameras[0], dict):
        camera_statuses = [camera['status'] for camera in cameras]
    else:
        camera_statuses = [camera.status for camera in cameras]
    recent_incidents = Incident.objects.select_related('reported_by')[:5]
    context = {
        **base_context,
        'camera_stats': {
            'total': len(cameras),
            'active': camera_statuses.count('active'),
            'inactive': camera_statuses.count('inactive'),
            'maintenance': camera_statuses.count('maintenance'),
        },
        'open_incidents': Incident.objects.exclude(status='resolved').count(),
        'recent_incidents': recent_incidents,
    }
    return render(request, 'security/dashboard.html', context)


@login_required
def security_cctv_view(request, base_context=None):
    base_context = base_context or {}
    cameras = list(Camera.objects.all())
    if not cameras:
        cameras = MOCK_CAMERAS
    context = {**base_context, 'cameras': cameras}
    return render(request, 'security/cctv.html', context)


@login_required
def security_incident_view(request, base_context=None):
    base_context = base_context or {}
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reported_by = request.user
            incident.save()
            messages.success(request, 'Incident logged successfully.')
            return redirect('a_home:security_page', page='incident')
    else:
        form = IncidentForm()

    context = {
        **base_context,
        'incident_form': form,
        'incidents': Incident.objects.select_related('reported_by').all(),
        'status_choices': Incident.STATUS_CHOICES,
    }
    return render(request, 'security/incident.html', context)
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
            if assigned_id: task.assigned_to_id = assigned_id
            task.save()

            # --- แจ้งเตือน: เมื่อนิติอัปเดตงานซ่อม ---
            # เปลี่ยนเป็น task.resident และ task.title ให้ตรงกับโมเดลที่นาดีนใช้นะครับ
            Notification.objects.create(
                user=task.resident,  
                title="อัปเดตสถานะงานซ่อม",
                message=f"งาน '{task.title}' ของคุณถูกเปลี่ยนสถานะเป็น: {task.get_status_display()}"
            )

            messages.success(request, 'อัปเดตข้อมูลงานซ่อมสำเร็จ')
            return redirect('a_home:juristic_page', page='maintenance')

    # ✨ พิกัดสำคัญ: ต้องเพิ่มก้อนนี้เข้าไปที่ท้ายฟังก์ชัน (อยู่นอก if POST)
    # เพื่อให้เวลาเรากด Tab เข้ามาดู (GET) Django จะได้รู้ว่าต้องวาดหน้าไหนออกมา
    context = {
        **base_context, 
        'tasks': tasks, 
        'status_choices': MaintenanceRequest.STATUS_CHOICES, 
        'priority_choices': MaintenanceRequest.PRIORITY_CHOICES, 
        'staff_users': User.objects.filter(is_staff=True)
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
        if not user.is_superuser:
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = new_role
            profile.save()
            user.is_active = active
            user.save()
            messages.success(request, f'อัปเดต {user.username} สำเร็จ')
        return redirect('a_home:juristic_page', page='users')
    context = {**base_context, 'users': User.objects.select_related('profile').all().order_by('-is_active'), 'role_choices': [('resident', 'ลูกบ้าน'), ('juristic', 'นิติบุคคล'), ('security', 'รปภ.')]}
    return render(request, 'juristic/user_roles.html', context)

@login_required
def billing_view(request, *args, **kwargs):
    role = 'juristic' if 'juristic' in request.path else 'resident'
    if request.method == 'POST':
        if 'create_invoice' in request.POST:
            unit, resident_id, amount, due_date = request.POST.get('unit'), request.POST.get('resident_id'), request.POST.get('amount'), request.POST.get('due_date')
            resident_user = get_object_or_404(User, id=resident_id)
            BillingInvoice.objects.create(unit=unit, resident=resident_user, tenant_name=resident_user.get_full_name() or resident_user.username, amount=amount, due_date=due_date, status='pending')
            
            # --- แจ้งเตือนของจริง: เมื่อนิติออกบิลใหม่ ---
            Notification.objects.create(
                user=resident_user,
                title="คุณมีบิลค่าใช้จ่ายใหม่",
                message=f"มียอดค้างชำระจำนวน {amount} บาท กำหนดชำระภายในวันที่ {due_date}"
            )
            
            messages.success(request, f'ออกบิลให้ห้อง {unit} เรียบร้อย!')
        elif 'update_status' in request.POST:
            invoice = get_object_or_404(BillingInvoice, pk=request.POST.get('invoice_id'))
            invoice.status = request.POST.get('status')
            if invoice.status == 'paid': invoice.paid_date = timezone.now().date()
            invoice.save()
            
            # ✨ แทรกโค้ดแจ้งเตือนตรงนี้ครับนาดีน:
            Notification.objects.create(
                user=invoice.resident,  # ส่งหาลูกบ้านเจ้าของบิล
                title="อัปเดตสถานะบิล",
                message=f"บิลของคุณได้รับการเปลี่ยนสถานะเป็น: {invoice.get_status_display()}"
            )
        elif 'upload_proof' in request.POST:
            invoice = get_object_or_404(BillingInvoice, pk=request.POST.get('invoice_id'), resident=request.user)
            slip = request.FILES.get('payment_proof')
            if slip:
                invoice.payment_proof, invoice.proof_uploaded_at, invoice.status = slip, timezone.now(), 'pending'
                invoice.save()
                
                # =========================================================
                juristic_users = User.objects.filter(profile__role='juristic', is_active=True)
                for juristic in juristic_users:
                    Notification.objects.create(
                        user=juristic,
                        title="💰 มีการแนบสลิปชำระเงินใหม่",
                        message=f"ห้อง {invoice.unit} ได้แนบสลิปชำระบิลยอด {invoice.amount} บาท"
                    )
                # =========================================================
                
        return redirect(request.path)

    invoices = BillingInvoice.objects.all().order_by('-id') if role == 'juristic' else BillingInvoice.objects.filter(resident=request.user).order_by('-id')
    context = {
        'invoices': invoices, 'user_role': role, 'status_choices': BillingInvoice.STATUS_CHOICES, 'active_tab': 'billing',
        'resident_users': User.objects.filter(is_staff=False) if role == 'juristic' else None, 'page_title': 'ระบบบัญชีและการเงิน'
    }
    return render(request, f'{role}/billing.html', context)
""""
@login_required
def monthly_report_view(request, base_context=None):
    base_context = base_context or {}
    if request.method == 'POST' and 'upload_report' in request.POST:
        form = MonthlyReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.uploaded_by = request.user
            report.save()
            return redirect('a_home:juristic_page', page='report')
        else:
          print("❌ Form is invalid!")
        print(f"Errors: {form.errors.as_data()}")
    context = {**base_context, 'reports': MonthlyReport.objects.all().order_by('-year', '-month'), 'report_form': MonthlyReportForm()}
    return render(request, 'juristic/monthly_reports.html', context)
"""

@login_required
def monthly_report_view(request, base_context=None):
    base_context = base_context or {}
    # สร้าง instance ของฟอร์มเปล่ารอไว้สำหรับกรณี GET request
    report_form = MonthlyReportForm()

    if request.method == 'POST' and 'upload_report' in request.POST:
        # นำข้อมูลที่ส่งมาใส่ในฟอร์ม
        report_form = MonthlyReportForm(request.POST, request.FILES)
        if report_form.is_valid():
            report = report_form.save(commit=False)
            report.uploaded_by = request.user
            report.save()
            return redirect('a_home:juristic_page', page='report')
        else:
            # หากฟอร์มไม่ถูกต้อง จะเก็บ Error ไว้ใน report_form และแสดงใน Terminal
            print("❌ Form is invalid!")
            print(f"Errors: {report_form.errors}")

    # ดึงรายการรายงานทั้งหมด และส่ง report_form ตัวที่มีข้อมูล (หรือ Error) กลับไป
    context = {
        **base_context, 
        'reports': MonthlyReport.objects.all().order_by('-year', '-month'), 
        'report_form': report_form
    }
    return render(request, 'juristic/monthly_reports.html', context)

# --- AI Chatbot Section ---
@login_required
def chat_room(request):
    return render(request, 'resident/chat_room.html')

@login_required
def chatbot_api(request):
    if request.method == 'POST':
        try:
            from groq import Groq

            data = json.loads(request.body)
            user_message = data.get('message', '')
            api_key = getattr(settings, 'GROQ_API_KEY', None)
            client = Groq(api_key=api_key)
            system_instructions = """
            คุณคือ 'น้องรื่นรมย์' AI ผู้ช่วยประจำคอนโด RuenPhiman 
            คุณคือ 'น้องรื่นรมย์' AI ผู้ช่วยประจำคอนโด RuenPhiman 
            บุคลิก: สุภาพ ใจดี ยิ้มแย้ม และพร้อมช่วยเหลือลูกบ้าน

            หน้าที่ของคุณคือ:
            1. หากลูกบ้านต้องการ 'แจ้งซ่อม' หรือ 'ซ่อมท่อน้ำ/ไฟ' ให้บอกขั้นตอนและให้ลิงก์นี้: /resident/repair_form/
            2. หากลูกบ้านต้องการ 'ดูประวัติแจ้งซ่อม' หรือ 'ติดตามงาน' ให้บอกลิงก์นี้: /resident/ticket/
            3. หากลูกบ้านต้องการ 'ดูบิล' หรือ 'จ่ายเงิน' ให้บอกลิงก์นี้: /resident/billing/
            4. หากถามเรื่องอื่นนอกเหนือจากนี้ ให้ตอบด้วยความสุภาพและแนะนำให้ติดต่อฝ่ายนิติบุคคลที่ชั้น 1

            คำเตือน: คุณต้องส่งลิงก์ในรูปแบบ HTML tag <a> เพื่อให้ลูกบ้านกดได้ เช่น <a href='/resident/repair_form/'>คลิกที่นี่เพื่อแจ้งซ่อม</a>
            """
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
            )
            reply_text = completion.choices[0].message.content
            return JsonResponse({'reply': reply_text})
        except Exception as e:
            return JsonResponse({'reply': f'เกิดข้อผิดพลาด: {str(e)}'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def upload_slip_view(request, request_id):
    if request.method == 'POST':
        maintenance_request = get_object_or_404(MaintenanceRequest, id=request_id, resident=request.user)
        slip_image = request.FILES.get('slip_image')
        if slip_image:
            maintenance_request.image = slip_image
            maintenance_request.status = 'verifying'
            maintenance_request.save()
            messages.success(request, 'ส่งหลักฐานการชำระเงินเรียบร้อยแล้ว!')
        return redirect('a_home:resident_page', page='ticket')\

def get_notifications_count(request):
    if request.user.is_authenticated:
        # ❌ ห้ามใช้ is_seen
        # ✅ ต้องใช้ is_read เท่านั้น ตามที่ Error แจ้งมาครับ
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        count = 0
    # ส่ง count ไปที่หน้ากระดิ่ง
    return render(request, 'partials/notifications_bell.html', {'count': count})
# 📍 พิกัด: a_home/views.py

def notification_list_view(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        
        # ✨ เพิ่มส่วนนี้: ดึง role ของผู้ใช้ส่งไปด้วย เพื่อให้ Template เลือกลิงก์ได้ถูกหน้า
        user_role = get_user_role(request.user)
        
        # ตรงนี้คือจุดที่เราเพิ่งเพิ่มไปเพื่อทำให้เลขสีแดงหายเมื่อกดดู
        # ต้องใช้ is_read=False และ .update(is_read=True) นะครับ
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    else:
        notifications = []
        user_role = 'resident' # ค่าเริ่มต้นสำหรับกรณีไม่ได้ Login
        
    return render(request, 'partials/notification_dropdown.html', {
        'notifications': notifications,
        'user_role': user_role  # ✅ ส่งค่านี้ไปเพื่อให้ HTML {% if user_role == 'juristic' %} ทำงานได้ครับ
    })

# ใน views.py ของหน้า Juristic ตอนเซฟสถานะ
def update_task_status(request, task_id):
    task = get_object_or_404(MaintenanceRequest, id=task_id)
    # ... โค้ดอัปเดตสถานะเดิม ...
    
    if task_saved:
        # สร้างแจ้งเตือนส่งไปให้ลูกบ้านที่เป็นเจ้าของห้อง
        Notification.objects.create(
            user=task.user,  # ส่งให้เจ้าของคำร้อง
            message=f"คำร้อง '{task.task}' ของคุณได้รับการอัปเดตเป็น: {task.get_status_display()}"
        )
    return redirect(...)

# ใน views.py (ฟังก์ชันที่นิติกดยืนยันยอดเงินเพื่อรองรับการแจ้งเตือนที่ลูกบ้าน)
def confirm_payment(request, invoice_id):
    invoice = get_object_or_404(BillingInvoice, id=invoice_id)
    # ... โค้ดอัปเดตสถานะบิลเดิม
    invoice.status = 'Paid' 
    invoice.save()

    # 🔔 สร้างแจ้งเตือนส่งให้ลูกบ้านเจ้าของบิล
    Notification.objects.create(
        user=invoice.user, # ส่งให้ลูกบ้านคนที่เป็นเจ้าของบิลนี้
        message=f"บิลรอบเดือน {invoice.month} ของคุณได้รับการยืนยันการชำระเงินแล้วครับ"
    )
    return redirect(...)
