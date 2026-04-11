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
    
    # 📌 ดักจับ Role ที่ไม่ถูกต้อง
    if user_role != role:
        if user_role == 'juristic':
            return redirect('juristic_page', page='dashboard')
        elif user_role == 'security':
            return redirect('security_page', page='dashboard')
        else:
            return redirect('resident_page', page='chatbot')

    # 📌 ดักจับ POST จากหน้า 'repair_form'
    if request.method == 'POST' and role == 'resident' and page == 'repair_form':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        
        if title and description:
            MaintenanceTicket.objects.create(
                resident=request.user,
                title=title,
                description=description,
                image=image
            )
            # พอบันทึกเสร็จ เด้งไปหน้าติดตามสถานะของซอลด้า
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
        'repair_form': 'Repair Form',
    }

    context = {
        'active_tab': page,
        'page_title': page_titles.get(page, page.title())
    }
    
    return render(request, f'{role}/{page}.html', context)