from django.db import models
from django.conf import settings
from a_users.adapters import User

class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอดำเนินการ'),
        ('in_progress', 'กำลังดำเนินการ'),
        ('waiting_payment', 'รอชำระเงิน'),
        ('verifying', 'รอตรวจสอบยอดเงิน'),
        ('completed', 'เสร็จสิ้น'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    image = models.ImageField(upload_to='maintenance_issues/', null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    slip_image = models.ImageField(upload_to='slips/', null=True, blank=True)
    payment_status = models.CharField(max_length=20, default='unpaid')

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
class Payment(models.Model):
    request = models.OneToOneField(MaintenanceRequest, on_delete=models.CASCADE, related_name='payment')
    slip_image = models.ImageField(upload_to='slips/')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
class Billing(models.Model):
    PAYMENT_STATUS = (
        ('unpaid', 'ยังไม่ชำระ'),
        ('checking', 'รอตรวจสอบสลิป'),
        ('paid', 'ชำระเงินแล้ว'),
    )
    
    resident = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200) # เช่น ค่าซ่อมไฟ, ค่าส่วนกลางเดือน เม.ย.
    amount = models.DecimalField(max_digits=10, decimal_places=2) # ยอดเงิน
    details = models.TextField(blank=True, null=True)
    slip_image = models.ImageField(upload_to='slips/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.resident.username}"