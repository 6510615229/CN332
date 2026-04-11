# เพิ่มโค้ดนี้ต่อท้ายไฟล์ views.py
@login_required
def submit_ticket(request):
    if request.method == 'POST':
        # 1. รับค่าที่เพื่อนตั้งชื่อไว้ในหน้าฟอร์ม (ตัวอย่าง: 'title', 'description')
        req_title = request.POST.get('title')
        req_desc = request.POST.get('description')
        
        # 2. เอาข้อมูลมาสร้างลง Database ทันที
        MaintenanceRequest.objects.create(
            resident=request.user,  # ดึงชื่อคนที่ล็อกอินอยู่มาเป็นเจ้าของรายการอัตโนมัติ
            title=req_title,
            description=req_desc,
            status='pending'  # บังคับสถานะเริ่มต้นเป็น "รอดำเนินการ" ทันที
        )
        
        # 3. เซฟเสร็จปุ๊บ ให้เด้งไปหน้า Tracking ที่คุณทำไว้เลย
        return redirect('maintenance-tracking')
        
    # ถ้าไม่ใช่การส่งฟอร์ม (กดเข้ามาดูเฉยๆ) ให้โชว์หน้าฟอร์มของเพื่อน
    # (เปลี่ยน 'ชื่อไฟล์ฟอร์มของเพื่อน.html' เป็นชื่อไฟล์จริงที่เพื่อนทำ)
    return render(request, 'ชื่อไฟล์ฟอร์มของเพื่อน.html')