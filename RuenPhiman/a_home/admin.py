from django.contrib import admin
from .models import MaintenanceRequest, BillingInvoice, MonthlyReport

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    # พี่แก้ created_by เป็น resident ให้ตรงกับ Model จริงๆ เพื่อกัน Error ครับ
    list_display = ('title', 'status', 'priority', 'assigned_to', 'resident', 'due_date', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')

@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'month', 'year', 'uploaded_by', 'uploaded_at')
    list_filter = ('year', 'month')
    search_fields = ('title',)

@admin.register(BillingInvoice)
class BillingInvoiceAdmin(admin.ModelAdmin):
    list_display = ('unit', 'tenant_name', 'resident', 'amount', 'due_date', 'paid_date', 'status', 'payment_proof')
    list_filter = ('status', 'due_date')
    search_fields = ('unit', 'tenant_name')