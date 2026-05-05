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
]
