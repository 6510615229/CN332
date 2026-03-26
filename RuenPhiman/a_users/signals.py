from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)       
def user_postsave(sender, instance, created, **kwargs):
    user = instance
    
    # add profile if user is created
    if created:
        Profile.objects.create(
            user = user,
        )
    else:
        # update allauth emailaddress if exists 
        try:
            email_address = EmailAddress.objects.get_primary(user)
            if email_address and email_address.email != user.email:
                email_address.email = user.email
                email_address.verified = False
                email_address.save()
        except EmailAddress.DoesNotExist:
            # --- แก้ตรงนี้ครับ ---
            # ถ้าหา EmailAddress ไม่เจอ "ห้ามสร้างใหม่เด็ดขาด" ให้ปล่อยผ่านไป (pass)
            # เพราะ django-allauth จะเป็นคนจัดการสร้างให้เองในกระบวนการของมัน
            pass
        
        
@receiver(pre_save, sender=User)
def user_presave(sender, instance, **kwargs):
    if instance.username:
        instance.username = instance.username.lower()