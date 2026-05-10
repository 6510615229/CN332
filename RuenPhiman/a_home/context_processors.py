from .models import Notification
from django.db import connection

def notifications_processor(request):
    """
    ดึงข้อมูลการแจ้งเตือนส่งไปให้ทุก Template 
    โดยมีการดัก Error กรณีที่ยังไม่ได้ Migrate ตาราง Notification
    """
    if request.user.is_authenticated:
        try:
            # เช็กก่อนว่ามีตาราง Notification อยู่ในฐานข้อมูลจริงไหม
            # (Django จะสร้างชื่อตารางเป็น 'ชื่อแอป_ชื่อโมเดล' เช่น a_home_notification)
            if 'a_home_notification' in connection.introspection.table_names():
                notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
                unread_count = notifications.filter(is_read=False).count()
                return {
                    'notifications': notifications,
                    'unread_notifications_count': unread_count
                }
        except Exception:
            # ถ้าเกิด Error ใดๆ (เช่น ตารางยังไม่มี) ให้ส่งค่าว่างกลับไป
            pass
            
    # กรณีไม่ได้ Login หรือยังไม่มีตาราง ให้แสดงผลเป็นค่าว่าง
    return {
        'notifications': [],
        'unread_notifications_count': 0
    }