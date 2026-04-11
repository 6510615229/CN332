from django.db import models
from django.conf import settings

class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'รอดำเนินการ'),
        ('in_progress', 'กำลังดำเนินการ'),
        ('waiting_payment', 'รอชำระเงิน'),
        ('verifying', 'รอตรวจสอบยอดเงิน'),
        ('completed', 'เสร็จสิ้น'),
    ]
    
    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class Payment(models.Model):
    request = models.OneToOneField(MaintenanceRequest, on_delete=models.CASCADE, related_name='payment')
    slip_image = models.ImageField(upload_to='slips/')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)