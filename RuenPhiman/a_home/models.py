from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings


# 1. ระบบแจ้งซ่อม (รวมจาก MaintenanceTicket และ MaintenanceTask)
class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอดำเนินการ'),
        ('in_progress', 'กำลังดำเนินการ'),
        ('completed', 'เสร็จสิ้น'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'ต่ำ'),
        ('medium', 'ปานกลาง'),
        ('high', 'สูง'),
    ]

    # ฟิลด์สำหรับลูกบ้าน
    resident = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_requests', verbose_name='ผู้แจ้ง (ลูกบ้าน)') 
    title = models.CharField(max_length=200, verbose_name='หัวข้อการแจ้ง') 
    description = models.TextField(verbose_name='รายละเอียด') 
    image = models.ImageField(upload_to='maintenance_images/', blank=True, null=True, verbose_name='รูปภาพประกอบ') 
    
    # ฟิลด์สำหรับนิติบุคคล
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='สถานะ')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='ลำดับความสำคัญ')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance', verbose_name='ช่างที่รับผิดชอบ') 
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name='วันที่แจ้ง')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='อัปเดตล่าสุด')
    due_date = models.DateField(null=True, blank=True, verbose_name='กำหนดเสร็จ')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'การแจ้งซ่อม'
        verbose_name_plural = 'การแจ้งซ่อม'

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title} - {self.resident.username}"


# 2. ระบบบิลค่าใช้จ่าย (Billing)
class BillingInvoice(models.Model):
    STATUS_CHOICES = (
        ('pending', 'รอชำระ'),
        ('paid', 'ชำระแล้ว'),
        ('overdue', 'เกินกำหนด'),
    )

    unit = models.CharField(max_length=20, verbose_name='หน่วย/ห้อง')
    tenant_name = models.CharField(max_length=100, verbose_name='ชื่อลูกบ้าน')
    resident = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_invoices', verbose_name='บัญชีผู้ใช้งาน')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='จำนวนเงิน')
    due_date = models.DateField(verbose_name='วันครบกำหนด')
    paid_date = models.DateField(null=True, blank=True, verbose_name='วันชำระ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='สถานะ')
    
    # ส่วนอัปโหลดสลิป
    payment_proof = models.ImageField(upload_to='billing_proofs/', null=True, blank=True, verbose_name='หลักฐานการชำระ (สลิป)')
    proof_uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_proofs', verbose_name='ผู้ส่งหลักฐาน')
    proof_uploaded_at = models.DateTimeField(null=True, blank=True, verbose_name='เวลาที่ส่งหลักฐาน')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-due_date']
        verbose_name = 'ใบแจ้งหนี้'
        verbose_name_plural = 'ใบแจ้งหนี้'

    def __str__(self):
        return f"{self.unit} - {self.tenant_name} ({self.get_status_display()})"


# 3. รายงานประจำเดือน (Monthly Report)
class MonthlyReport(models.Model):
    title = models.CharField(max_length=200, verbose_name='หัวข้อรายงาน')
    file = models.FileField(upload_to='monthly_reports/', verbose_name='ไฟล์รายงาน')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='อัปโหลดโดย')
    uploaded_at = models.DateTimeField(default=timezone.now, verbose_name='วันที่อัปโหลด')
    month = models.IntegerField(verbose_name='เดือน (1-12)')
    year = models.IntegerField(verbose_name='ปี (ค.ศ.)')

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['month', 'year']
        verbose_name = 'รายงานประจำเดือน'
        verbose_name_plural = 'รายงานประจำเดือน'

    def __str__(self):
        return f"{self.title} ({self.month}/{self.year})"