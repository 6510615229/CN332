# a_home/urls.py
from django.urls import path
from . import views

urlpatterns =[
    path('', views.home_view, name='home'),
    
    # ใช้ View เดียวกัน แต่ส่งค่า role แยกกันไป
    path('juristic/<str:page>/', views.role_page_view, {'role': 'juristic'}, name='juristic_page'),
    path('security/<str:page>/', views.role_page_view, {'role': 'security'}, name='security_page'),
    path('resident/<str:page>/', views.role_page_view, {'role': 'resident'}, name='resident_page'),
]