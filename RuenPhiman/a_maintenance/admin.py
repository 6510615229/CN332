from django.contrib import admin
from .models import MaintenanceRequest, Payment

# สั่งให้ MaintenanceRequest โชว์ในหน้า Admin
admin.site.register(MaintenanceRequest)

# สั่งให้ Payment (ข้อมูลการโอนเงิน) โชว์ในหน้า Admin
admin.site.register(Payment)