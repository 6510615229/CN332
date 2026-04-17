from django import forms
from .models import MaintenanceTicket, BillingInvoice, MonthlyReport

class MaintenanceTaskForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTicket
        fields = ['title', 'description', 'priority', 'assigned_to', 'due_date', 'status']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class BillingProofForm(forms.Form):
    invoice_id = forms.IntegerField(widget=forms.HiddenInput)
    payment_proof = forms.FileField(
        label='หลักฐานการชำระเงิน',
        widget=forms.FileInput(attrs={'accept': 'image/*,application/pdf'})
    )

class MonthlyReportForm(forms.ModelForm):
    class Meta:
        model = MonthlyReport
        fields = ['title', 'file', 'month', 'year']
        widgets = {
            'month': forms.NumberInput(attrs={'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'min': 2020, 'max': 2030}),
        }
