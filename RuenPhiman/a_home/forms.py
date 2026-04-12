from django import forms

from .models import MaintenanceTask, MonthlyReport


class MaintenanceTaskForm(forms.ModelForm):
    class Meta:
        model = MaintenanceTask
        fields = ['title', 'description', 'priority', 'status', 'due_date', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border border-slate-300 bg-white py-2 px-3 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'description': forms.Textarea(attrs={
                'rows': 2,
                'class': 'mt-1 block w-full rounded-lg border border-slate-300 bg-white py-2 px-3 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'priority': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-lg border border-slate-300 bg-white py-2 px-3 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'status': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-lg border border-slate-300 bg-white py-2 px-3 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 block w-full rounded-lg border border-slate-300 bg-white py-2 px-3 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'mt-1 block w-full rounded-lg border border-slate-300 bg-white py-2 px-3 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
        }


from datetime import date


class BillingProofForm(forms.Form):
    invoice_id = forms.IntegerField(widget=forms.HiddenInput())
    payment_proof = forms.FileField(
        label='Upload PDF',
        widget=forms.ClearableFileInput(attrs={
            'class': 'mt-1 block w-full text-sm text-slate-700',
            'accept': 'application/pdf',
        })
    )


class MonthlyReportForm(forms.ModelForm):
    report_month = forms.DateField(
        required=True,
        label='Month/Year',
        input_formats=['%Y-%m'],
        widget=forms.DateInput(attrs={
            'type': 'month',
            'class': 'mt-1 block w-full rounded-lg border border-slate-300 bg-white py-2 px-3 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
        }),
    )

    class Meta:
        model = MonthlyReport
        fields = ['title', 'file', 'report_month']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-lg border border-slate-300 bg-white py-2 px-3 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'mt-1 block w-full text-sm text-slate-700',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.month and self.instance.year:
            self.initial['report_month'] = date(self.instance.year, self.instance.month, 1)

    def save(self, commit=True):
        report_month = self.cleaned_data.get('report_month')
        if report_month:
            self.instance.month = report_month.month
            self.instance.year = report_month.year
        return super().save(commit=commit)
