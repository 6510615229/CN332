from django.db import models

# Create your models here.

from django.contrib.auth.models import User

class MaintenanceTicket(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'รอดำเนินการ'),
        ('In Progress', 'กำลังซ่อม'),
        ('Done', 'เสร็จสิ้น'),
    ]
    
    # เชื่อมกับ User ว่าลูกบ้านคนไหนเป็นคนแจ้ง
    resident = models.ForeignKey(User, on_delete=models.CASCADE) 
    title = models.CharField(max_length=200) 
    description = models.TextField() 
    image = models.ImageField(upload_to='maintenance_images/', blank=True, null=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.status}] {self.title} - {self.resident.username}"