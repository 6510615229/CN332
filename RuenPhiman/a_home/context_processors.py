# a_home/context_processors.py
from .models import Notification

def notifications_processor(request):
    # ตรวจสอบว่า User login หรือยังก่อนดึงข้อมูล
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
            unread_count = notifications.filter(is_read=False).count()
            return {
                'notifications': notifications,
                'unread_notifications_count': unread_count
            }
        except:
            # กันเหนื่อยถ้า Database ยังไม่มีตาราง Notification
            return {
                'notifications': [],
                'unread_notifications_count': 0
            }
    return {
        'notifications': [],
        'unread_notifications_count': 0
    }