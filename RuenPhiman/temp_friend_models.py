from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MaintenanceTask(models.Model):
    STATUS_CHOICES = (
        ('pending', 'รอดำเนินการ'),
        ('in_progress', 'กำลังดำเนินการ'),
        ('completed', 'เสร็จสิ้น'),
    )

    PRIORITY_CHOICES = (
        ('low', 'ต่ำ'),
        ('medium', 'ปานกลาง'),
        ('high', 'สูง'),
    )

    title = models.CharField(max_length=200, verbose_name='หัวข้อ')
    description = models.TextField(blank=True, verbose_name='รายละเอียด')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='สถานะ')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='ลำดับความสำคัญ')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name='สร้างโดย')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks', verbose_name='มอบหมายให้')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='วันที่สร้าง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='วันที่อัปเดต')
    due_date = models.DateField(null=True, blank=True, verbose_name='วันที่ครบกำหนด')

    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = 'งานซ่อมบำรุง'
        verbose_name_plural = 'งานซ่อมบำรุง'

    def __str__(self):
        return self.title

class MonthlyReport(models.Model):
    title = models.CharField(max_length=200, verbose_name='หัวข้อรายงาน')
    file = models.FileField(upload_to='monthly_reports/', verbose_name='ไฟล์รายงาน')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='อัปโหลดโดย')
    uploaded_at = models.DateTimeField(default=timezone.now, verbose_name='วันที่อัปโหลด')
    month = models.IntegerField(verbose_name='เดือน')
    year = models.IntegerField(verbose_name='ปี')

    class Meta:
        ordering = ['-year', '-month']
        verbose_name = 'รายงานประจำเดือน'
        verbose_name_plural = 'รายงานประจำเดือน'
        unique_together = ['month', 'year']

    def __str__(self):
        return f"{self.title} - {self.month}/{self.year}"


class BillingInvoice(models.Model):
    STATUS_CHOICES = (
        ('pending', 'ค้างชำระ'),
        ('paid', 'ชำระแล้ว'),
        ('overdue', 'เลยกำหนด'),
    )

    unit = models.CharField(max_length=20, verbose_name='ห้อง')
    tenant_name = models.CharField(max_length=100, verbose_name='ชื่อผู้เช่า')
    resident = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_invoices', verbose_name='ผู้เช่า')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='จำนวนเงิน')
    due_date = models.DateField(verbose_name='วันครบกำหนด')
    paid_date = models.DateField(null=True, blank=True, verbose_name='วันชำระ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='สถานะ')
    payment_proof = models.FileField(upload_to='billing_proofs/', null=True, blank=True, verbose_name='หลักฐานการชำระ')
    proof_uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_proofs', verbose_name='ผู้ส่งหลักฐาน')
    proof_uploaded_at = models.DateTimeField(null=True, blank=True, verbose_name='วันที่ส่งหลักฐาน')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='วันที่สร้าง')

    class Meta:
        ordering = ['-due_date']
        verbose_name = 'ใบแจ้งหนี้'
        verbose_name_plural = 'ใบแจ้งหนี้'

    def __str__(self):
        return f"{self.unit} - {self.tenant_name} ({self.status})"
