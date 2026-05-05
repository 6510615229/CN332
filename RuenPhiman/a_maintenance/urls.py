from django.urls import path
# เพิ่ม submit_ticket เข้าไปในบรรทัด import ด้านล่างนี้ครับ
from .views import tracking_view, upload_slip, submit_ticket 

urlpatterns = [
    path('tracking/', tracking_view, name='maintenance-tracking'),
    path('upload-slip/<int:pk>/', upload_slip, name='upload-slip'),
    path('submit/', submit_ticket, name='submit-ticket'),
]