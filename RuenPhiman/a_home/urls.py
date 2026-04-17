from django.urls import path
from . import views

app_name = 'a_home'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('juristic/<str:page>/', views.role_page_view, {'role': 'juristic'}, name='juristic_page'),
    path('security/<str:page>/', views.role_page_view, {'role': 'security'}, name='security_page'),
    path('resident/<str:page>/', views.role_page_view, {'role': 'resident'}, name='resident_page'),
]
