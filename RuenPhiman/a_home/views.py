# a_home/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import MaintenanceTicket

# ฟังก์ชันตัวช่วย: จัดการกรณี User เก่าที่ role เป็นค่าว่างหรือเกิด Error
def get_user_role(user):
    try:
        role = user.profile.role
        if role: # ถ้ามีค่า ('juristic', 'security', 'resident') ให้คืนค่านั้น
            return role
    except:
        pass
    # ถ้า role เป็นค่าว่าง หรือไม่มี Profile ให้บังคับเป็นลูกบ้าน (resident) ทันที
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
    
    # ถ้า Role ของ User ไม่ตรงกับ URL ที่พยายามเข้า (เช่น ลูกบ้านพิมพ์ URL เข้าหน้านิติ)
    # เราจะไม่ส่งกลับไปหน้า home แล้วเพื่อป้องกัน Loop
    # แต่จะบังคับเตะกลับไปหน้าแรกของ Role ตัวเองแทน
    if user_role != role:
        if user_role == 'juristic':
            return redirect('juristic_page', page='dashboard')
        elif user_role == 'security':
            return redirect('security_page', page='dashboard')
        else:
            return redirect('resident_page', page='chatbot')

    if request.method == 'POST' and role == 'resident' and page == 'chatbot':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image') # รับไฟล์รูปภาพ
        
        if title and description:
            MaintenanceTicket.objects.create(
                resident=request.user,
                title=title,
                description=description,
                image=image
            )
            # เมื่อส่งเสร็จ ให้เด้งไปหน้า Ticket Tracking (งานที่ซอลด้ากำลังทำ) 
            return redirect('resident_page', page='ticket')

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
    }

    context = {
        'active_tab': page,
        'page_title': page_titles.get(page, page.title())
    }
    return render(request, 'role_layout.html', context)