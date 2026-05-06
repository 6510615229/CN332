from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from a_home import views
from a_users.views import profile_view
from a_home.views import mark_notification_as_read


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('a_home.urls')), # <--- ตัวนี้จะไปดึงหน้าแชทมาให้เอง
    path('maintenance/', include('a_maintenance.urls')),
    path('profile/', include('a_users.urls')),
    path('@<username>/', profile_view, name="profile"),
    path('notifications/mark-as-read/<int:notification_id>/', mark_notification_as_read, name='navbar-notifications'),
    # สำหรับดึงข้อมูลไปอัปเดตตัวเลขกระดิ่ง (อันที่ HTMX เรียก)
    path('notifications/unread-count/', views.get_notifications_count, name='navbar-notifications'),

    # สำหรับกดอ่านแจ้งเตือนรายอัน (อันที่ต้องมี ID)
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark-notification-read'),
]


# ส่วนของ Debug ปล่อยไว้เหมือนเดิม
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]