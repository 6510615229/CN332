from django import forms
from .models import MaintenanceRequest, BillingInvoice, MonthlyReport
from datetime import date

# สไตล์ส่วนกลางสำหรับ Input
INPUT_CLASSES = 'mt-1 block w-full rounded-lg border border-slate-300 bg-white py-2 px-3 shadow-sm focus:border-indigo-500 focus:ring-indigo-500'

class MaintenanceTaskForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'description', 'priority', 'status', 'due_date', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': INPUT_CLASSES}),
            'priority': forms.Select(attrs={'class': INPUT_CLASSES}),
            'status': forms.Select(attrs={'class': INPUT_CLASSES}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASSES}),
            'assigned_to': forms.Select(attrs={'class': INPUT_CLASSES}),
        }

class BillingProofForm(forms.Form):
    invoice_id = forms.IntegerField(widget=forms.HiddenInput())
    payment_proof = forms.FileField(
        label='หลักฐานการชำระเงิน (รูปภาพ หรือ PDF)',
        widget=forms.ClearableFileInput(attrs={
            'class': 'mt-1 block w-full text-sm text-slate-700',
            'accept': 'image/*,application/pdf', # รับทั้งรูปและ PDF ตามที่คุณต้องการ
        })
    )

class MonthlyReportForm(forms.ModelForm):
    # รวม Month และ Year เป็น Field เดียวเพื่อให้เลือกง่ายแบบปฏิทิน
    report_month = forms.DateField(
        required=True,
        label='ประจำเดือน/ปี',
        input_formats=['%Y-%m'],
        widget=forms.DateInput(attrs={
            'type': 'month',
            'class': INPUT_CLASSES,
        }),
    )

    class Meta:
        model = MonthlyReport
        fields = ['title', 'file', 'report_month']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'file': forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full text-sm text-slate-700'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ถ้าเป็นการแก้ไขข้อมูล ให้ดึงค่า Month/Year เดิมมาแสดง
        if self.instance and self.instance.pk and self.instance.month and self.instance.year:
            self.initial['report_month'] = date(self.instance.year, self.instance.month, 1)

    def save(self, commit=True):
        report_month = self.cleaned_data.get('report_month')
        if report_month:
            self.instance.month = report_month.month
            self.instance.year = report_month.year
        return super().save(commit=commit)