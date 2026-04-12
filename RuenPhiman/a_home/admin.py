from django.contrib import admin

from .models import MaintenanceTask, MonthlyReport


@admin.register(MaintenanceTask)
class MaintenanceTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'assigned_to', 'created_by', 'due_date', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'month', 'year', 'uploaded_by', 'uploaded_at')
    list_filter = ('year', 'month')
    search_fields = ('title',)


from .models import BillingInvoice

@admin.register(BillingInvoice)
class BillingInvoiceAdmin(admin.ModelAdmin):
    list_display = ('unit', 'tenant_name', 'resident', 'amount', 'due_date', 'paid_date', 'status', 'payment_proof')
    list_filter = ('status', 'due_date')
    search_fields = ('unit', 'tenant_name')
