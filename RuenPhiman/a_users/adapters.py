#a_users/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.shortcuts import resolve_url

from django.contrib.auth import get_user_model
User = get_user_model()

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_signup_redirect_url(self, request):
        return resolve_url("profile-onboarding")
    
    def get_login_redirect_url(self, request):
        user = request.user
        if hasattr(user, 'profile'):
            role = user.profile.role
            if role == 'juristic':
                return resolve_url('juristic_page', page='dashboard')
            elif role == 'security':
                return resolve_url('security_page', page='dashboard')
            else:
                return resolve_url('resident_page', page='chatbot')
        return resolve_url('home')
    
    
class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.account.extra_data.get("email")
        
        if not email:
            return
        
        if not sociallogin.is_existing:
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                sociallogin.connect(request, existing_user)
        
        if sociallogin.is_existing: 
            user = sociallogin.user
            email_address, created = EmailAddress.objects.get_or_create(user=user, email=email)
            if not email_address.verified:
                email_address.verified = True
                email_address.save()
                
                
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        
        email = user.email
        if email:
            email_address, created = EmailAddress.objects.get_or_create(user=user, email=email)
            if not email_address.verified:
                email_address.verified = True
                email_address.save()
            
        extra_data = sociallogin.account.extra_data
        display_name = ""
        
        if sociallogin.account.provider == 'line':
            display_name = extra_data.get('name') or extra_data.get('displayName', '')
        elif sociallogin.account.provider == 'google':
            display_name = extra_data.get('name', '')
        elif sociallogin.account.provider == 'github':
            display_name = extra_data.get('name') or extra_data.get('login', '')

        if display_name:
            user.profile.displayname = display_name.strip()
            user.profile.save()
            
        return user
    
    def populate_user(self, request, sociallogin, data):
        return super().populate_user(request, sociallogin, data)