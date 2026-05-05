from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MaintenanceRequest

# 1. หน้าแสดงรายการที่แจ้งซ่อม (Tracking)
@login_required
def tracking_view(request):
    # ดึงเฉพาะรายการแจ้งซ่อมของคนที่ล็อกอินอยู่
    tickets = MaintenanceRequest.objects.filter(resident=request.user).order_by('-id')
    
    #สร้าง context เพื่อส่งตัวแปรไปให้ HTML
    context = {
        'requests': tickets,  # เปลี่ยน key เป็น 'requests' ให้ตรงกับใน HTML
        'active_tab': 'ticket', # ใส่เพื่อให้เมนู Sidebar ติดไฮไลต์สี
    }
    
    return render(request, 'a_maintenance/tracking.html', context)

# 2. หน้าแบบฟอร์มและการส่งข้อมูล (Submit)
@login_required
def submit_ticket(request):
    if request.method == 'POST':
        # รับค่าจากฟอร์ม
        req_title = request.POST.get('title')
        req_desc = request.POST.get('description')
        
        # ตรวจสอบเบื้องต้นว่ามีข้อมูลไหม
        if req_title and req_desc:
            MaintenanceRequest.objects.create(
                resident=request.user,
                title=req_title,
                description=req_desc,
                status='pending'
            )
            messages.success(request, 'ส่งเรื่องแจ้งซ่อมเรียบร้อยแล้ว!')
            return redirect('maintenance-tracking')
        else:
            messages.error(request, 'กรุณากรอกข้อมูลให้ครบถ้วน')
        
    return render(request, 'a_maintenance/repair_form.html')

# 3. ฟังก์ชันสำหรับอัปโหลดสลิป (แก้ไขให้รับ pk ตาม urls.py)
@login_required
def upload_slip(request, pk):
    # ดึงข้อมูล Ticket นั้นๆ มาแสดงหรือตรวจสอบ
    ticket = get_object_or_404(MaintenanceRequest, pk=pk, resident=request.user)
    
    if request.method == 'POST':
        # ตัวอย่าง Logic การอัปโหลดไฟล์ (ถ้า Model ของคุณมีฟิลด์ slip)
        # slip_file = request.FILES.get('slip_image')
        # if slip_file:
        #     ticket.slip = slip_file
        #     ticket.save()
        #     messages.success(request, 'อัปโหลดสลิปสำเร็จ!')
        #     return redirect('maintenance-tracking')
        pass

    return render(request, 'a_maintenance/upload_slip.html', {'ticket': ticket})