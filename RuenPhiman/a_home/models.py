from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MaintenanceTicket(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอดำเนินการ'),
        ('in_progress', 'กำลังดำเนินการ'),
        ('completed', 'เสร็จสิ้น'),
        ('Pending', 'รอดำเนินการ'),      # รองรับข้อมูลเก่า
        ('In Progress', 'กำลังซ่อม'),     # รองรับข้อมูลเก่า
        ('Done', 'เสร็จสิ้น'),             # รองรับข้อมูลเก่า
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'ต่ำ'),
        ('medium', 'ปานกลาง'),
        ('high', 'สูง'),
    ]

    resident = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets') 
    title = models.CharField(max_length=200) 
    description = models.TextField() 
    image = models.ImageField(upload_to='maintenance_images/', blank=True, null=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.status}] {self.title} - {self.resident.username}"


class BillingInvoice(models.Model):
    STATUS_CHOICES = (
        ('pending', 'รอชำระ'),
        ('paid', 'ชำระแล้ว'),
        ('overdue', 'เกินกำหนด'),
    )

    unit = models.CharField(max_length=20, verbose_name='หน่วย')
    tenant_name = models.CharField(max_length=100, verbose_name='ชื่อผู้เช่า/ลูกบ้าน')
    resident = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_invoices')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='จำนวนเงิน')
    due_date = models.DateField(verbose_name='วันครบกำหนด')
    paid_date = models.DateField(null=True, blank=True, verbose_name='วันชำระ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_proof = models.FileField(upload_to='billing_proofs/', null=True, blank=True, verbose_name='หลักฐานการชำระ')
    proof_uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_proofs')
    proof_uploaded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-due_date']

    def __str__(self):
        return f"{self.unit} - {self.tenant_name} ({self.status})"


class MonthlyReport(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='monthly_reports/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(default=timezone.now)
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['month', 'year']

    def __str__(self):
        return f"{self.title} - {self.month}/{self.year}"
