from django.urls import path
from . import views

app_name = 'a_home'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('juristic/<str:page>/', views.role_page_view, {'role': 'juristic'}, name='juristic_page'),
    path('security/<str:page>/', views.role_page_view, {'role': 'security'}, name='security_page'),
    path('resident/<str:page>/', views.role_page_view, {'role': 'resident'}, name='resident_page'),
    path('chat-room/', views.chat_room, name='chat_room'),
    path('chatbot/api/', views.chatbot_api, name='chatbot_api'),
    path('upload-slip/<int:request_id>/', views.upload_slip_view, name='upload_slip'),
    
    # --- ส่วนของ Notification ---

    # 1. สำหรับอัปเดตตัวเลขแจ้งเตือนบนกระดิ่ง (HTMX hx-get ที่นาดีนเจอใน notifications_bell.html)
    path('notifications/unread-count/', views.get_notifications_count, name='navbar-notifications'),

    # 2. สำหรับดึงรายการแจ้งเตือนมาโชว์ใน Dropdown (ชื่อต้องตรงกับ notification-list ที่ Error ฟ้อง)
    path('notifications/dropdown/', views.notification_list_view, name='notification-list'),

    # 3. สำหรับกดอ่านแจ้งเตือน (Mark as read)
    # หมายเหตุ: นาดีนสามารถเลือกใช้ name ไหนก็ได้ใน Template แต่ในที่นี้ผมรวมเป็นชื่อเดียวให้ไม่งงครับ
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark-notification-read'),
]