from django import forms

from .models import MaintenanceTask, MonthlyReport


class MaintenanceTaskForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTask
        fields = ['title', 'description', 'priority', 'status', 'due_date', 'assigned_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


class MonthlyReportForm(forms.ModelForm):
    class Meta:
        model = MonthlyReport
        fields = ['title', 'file', 'month', 'year']
        widgets = {
            'month': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'min': 2000, 'max': 2100}),
        }
