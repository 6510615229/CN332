from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'displayname') # แสดงคอลัมน์ในหน้ารวม
    list_filter = ('role',) # เพิ่มตัวกรองค้นหาตาม Role ด้านขวามือ

admin.site.register(Profile, ProfileAdmin)
