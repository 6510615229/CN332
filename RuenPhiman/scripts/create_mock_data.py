import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'a_core.settings')
django.setup()

from django.contrib.auth.models import User
from a_home.models import MaintenanceTask

u = User.objects.filter(is_superuser=True).first() or User.objects.first()
if not u:
    u = User.objects.create_user('admin', password='admin123')

for i in range(1, 7):
    MaintenanceTask.objects.get_or_create(
        title=f'Mock Task #{i}',
        defaults={
            'description': f'This is mock maintenance task number {i}',
            'status': 'pending' if i % 3 == 1 else 'in_progress' if i % 3 == 2 else 'completed',
            'priority': 'high' if i % 3 == 0 else 'medium' if i % 3 == 1 else 'low',
            'created_by': u,
            'due_date': None,
        },
    )

print('Mock tasks created:', MaintenanceTask.objects.count())
