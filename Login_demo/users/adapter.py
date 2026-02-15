from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)

        if sociallogin.account.provider == 'line':
            # ดึงข้อมูลจาก log ที่คุณเจอ (ใช้ 'name' เป็นหลัก)
            extra_data = sociallogin.account.extra_data
            
            # หาชื่อจาก name หรือ displayName
            line_name = extra_data.get('name') or extra_data.get('displayName')
            
            if line_name:
                clean_name = line_name.strip()
                
                user.username = clean_name
        
        return user