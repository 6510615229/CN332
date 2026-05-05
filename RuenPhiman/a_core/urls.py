from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from a_users.views import profile_view
# ลบการ import * ของ a_home ออกเพื่อลดความสับสน

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('a_home.urls')), # <--- ตัวนี้จะไปดึงหน้าแชทมาให้เอง
    path('maintenance/', include('a_maintenance.urls')),
    path('profile/', include('a_users.urls')),
    path('@<username>/', profile_view, name="profile"),
]

# ส่วนของ Debug ปล่อยไว้เหมือนเดิม
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]