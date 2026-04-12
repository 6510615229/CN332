import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a_core.settings')
django.setup()

from django.contrib.auth.models import User
from a_users.models import Profile

# Change admin role
try:
    user = User.objects.get(username='admin')
    profile, created = Profile.objects.get_or_create(user=user)
    profile.role = 'juristic'  # Change to desired role: 'juristic', 'security', or 'resident'
    profile.save()
    print(f"Admin role updated to '{profile.role}'")
except User.DoesNotExist:
    print("Admin user not found. Create superuser first.")