from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # เขียนทับ username เดิมของ Django
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[],  # <-- จุดสำคัญ! ใส่ลิสต์ว่าง แปลว่า "พิมพ์อะไรมาก็ได้ รับหมด" (รวมถึง Space และ Emoji)
        error_messages={
            'unique': "ชื่อผู้ใช้นี้มีคนใช้แล้ว",
        },
    )
