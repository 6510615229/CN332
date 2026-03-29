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
