from datetime import timedelta

from django.utils import timezone


def get_seed_incidents():
    now = timezone.now()
    return [
        {
            'title': 'Unauthorized visitor at side gate',
            'description': 'Unknown visitor attempted entry without registration.',
            'location': 'Side Gate',
            'severity': 'high',
            'status': 'investigating',
            'occurred_at': now - timedelta(hours=2),
        },
        {
            'title': 'Parking barrier malfunction',
            'description': 'Vehicle barrier remained open longer than expected.',
            'location': 'Parking Entrance',
            'severity': 'medium',
            'status': 'open',
            'occurred_at': now - timedelta(hours=5),
        },
        {
            'title': 'Suspicious package reported',
            'description': 'Unattended package found near the mail room entrance.',
            'location': 'Mail Room',
            'severity': 'high',
            'status': 'resolved',
            'occurred_at': now - timedelta(days=1, hours=1),
        },
        {
            'title': 'Noise complaint from rooftop',
            'description': 'Residents reported loud activity after quiet hours.',
            'location': 'Rooftop Access',
            'severity': 'low',
            'status': 'resolved',
            'occurred_at': now - timedelta(days=1, hours=4),
        },
        {
            'title': 'Emergency exit door left open',
            'description': 'Door sensor showed prolonged open state.',
            'location': 'Floor 7 Stairwell',
            'severity': 'medium',
            'status': 'open',
            'occurred_at': now - timedelta(days=2),
        },
        {
            'title': 'Camera feed interruption',
            'description': 'Temporary signal loss detected from one hallway camera.',
            'location': 'Elevator Hall',
            'severity': 'medium',
            'status': 'investigating',
            'occurred_at': now - timedelta(days=2, hours=3),
        },
        {
            'title': 'Tailgating detected',
            'description': 'Two visitors entered behind one authorized resident.',
            'location': 'Main Entrance',
            'severity': 'high',
            'status': 'resolved',
            'occurred_at': now - timedelta(days=3, hours=2),
        },
        {
            'title': 'Water leak near electrical room',
            'description': 'Security patrol found water accumulation near service corridor.',
            'location': 'Basement Service Corridor',
            'severity': 'critical',
            'status': 'investigating',
            'occurred_at': now - timedelta(days=4),
        },
        {
            'title': 'Gym access after hours',
            'description': 'Access control recorded entry outside permitted hours.',
            'location': 'Fitness Center',
            'severity': 'low',
            'status': 'resolved',
            'occurred_at': now - timedelta(days=5, hours=6),
        },
        {
            'title': 'Delivery vehicle in restricted lane',
            'description': 'Vehicle stopped in emergency lane during unloading.',
            'location': 'Loading Bay',
            'severity': 'medium',
            'status': 'open',
            'occurred_at': now - timedelta(days=6),
        },
    ]
