from django.core.management.base import BaseCommand

from a_home.mock_incidents import get_seed_incidents
from a_home.models import Incident


class Command(BaseCommand):
    help = 'Seed the database with the initial incident log samples.'

    def handle(self, *args, **options):
        created_count = 0
        for incident_data in get_seed_incidents():
            _, created = Incident.objects.get_or_create(
                title=incident_data['title'],
                defaults=incident_data,
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created_count} incident sample(s).'))
