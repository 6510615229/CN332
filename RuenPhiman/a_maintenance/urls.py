from django.urls import path
from .views import tracking_view, upload_slip

urlpatterns = [
    path('tracking/', tracking_view, name='maintenance-tracking'),
    path('upload-slip/<int:pk>/', upload_slip, name='upload-slip'),
    path('submit/', submit_ticket, name='submit-ticket'),
]