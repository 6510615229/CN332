from datetime import date, timedelta
from decimal import Decimal

from django.utils import timezone


def get_seed_maintenance_requests():
    today = timezone.now()
    return [
        {'title': 'Leaking pipe in unit 1204', 'description': 'Resident reported water dripping under kitchen sink.', 'status': 'pending', 'priority': 'high', 'created_at': today - timedelta(days=1), 'due_date': date.today() + timedelta(days=1)},
        {'title': 'Hallway light replacement', 'description': 'Light fixture flickering on floor 8 corridor.', 'status': 'in_progress', 'priority': 'medium', 'created_at': today - timedelta(days=2), 'due_date': date.today() + timedelta(days=2)},
        {'title': 'Elevator button issue', 'description': 'Button for floor 5 intermittently unresponsive.', 'status': 'pending', 'priority': 'high', 'created_at': today - timedelta(days=3), 'due_date': date.today() + timedelta(days=1)},
        {'title': 'Air conditioner inspection', 'description': 'Unit 904 requested inspection for weak cooling.', 'status': 'completed', 'priority': 'medium', 'created_at': today - timedelta(days=4), 'due_date': date.today() - timedelta(days=1)},
        {'title': 'Pool deck cleaning', 'description': 'Additional cleaning requested after weekend use.', 'status': 'completed', 'priority': 'low', 'created_at': today - timedelta(days=5), 'due_date': date.today() - timedelta(days=2)},
        {'title': 'Parking gate sensor check', 'description': 'Gate opened slowly during morning rush.', 'status': 'in_progress', 'priority': 'high', 'created_at': today - timedelta(days=6), 'due_date': date.today() + timedelta(days=3)},
        {'title': 'Window latch repair', 'description': 'Loose latch reported in unit 703 bedroom.', 'status': 'pending', 'priority': 'low', 'created_at': today - timedelta(days=7), 'due_date': date.today() + timedelta(days=5)},
        {'title': 'Water pressure complaint', 'description': 'Low pressure reported on upper floors during evenings.', 'status': 'in_progress', 'priority': 'medium', 'created_at': today - timedelta(days=8), 'due_date': date.today() + timedelta(days=4)},
        {'title': 'Mailbox lock replacement', 'description': 'Mailbox lock jammed for resident in unit 305.', 'status': 'completed', 'priority': 'low', 'created_at': today - timedelta(days=9), 'due_date': date.today() - timedelta(days=3)},
        {'title': 'Generator inspection', 'description': 'Scheduled safety inspection for backup generator.', 'status': 'pending', 'priority': 'medium', 'created_at': today - timedelta(days=10), 'due_date': date.today() + timedelta(days=7)},
    ]


def get_seed_billing_invoices():
    today = date.today()
    return [
        {'unit': '101', 'tenant_name': 'Anan Chai', 'amount': Decimal('2450.00'), 'due_date': today - timedelta(days=12), 'paid_date': today - timedelta(days=10), 'status': 'paid'},
        {'unit': '204', 'tenant_name': 'Benjamas S.', 'amount': Decimal('2450.00'), 'due_date': today - timedelta(days=8), 'paid_date': None, 'status': 'overdue'},
        {'unit': '305', 'tenant_name': 'Chalida R.', 'amount': Decimal('2600.00'), 'due_date': today + timedelta(days=4), 'paid_date': None, 'status': 'pending'},
        {'unit': '402', 'tenant_name': 'Darin K.', 'amount': Decimal('2450.00'), 'due_date': today - timedelta(days=5), 'paid_date': today - timedelta(days=3), 'status': 'paid'},
        {'unit': '507', 'tenant_name': 'Ekkachai P.', 'amount': Decimal('2750.00'), 'due_date': today + timedelta(days=6), 'paid_date': None, 'status': 'pending'},
        {'unit': '608', 'tenant_name': 'Fahsai M.', 'amount': Decimal('2450.00'), 'due_date': today - timedelta(days=15), 'paid_date': None, 'status': 'overdue'},
        {'unit': '703', 'tenant_name': 'Garin T.', 'amount': Decimal('2450.00'), 'due_date': today - timedelta(days=2), 'paid_date': today - timedelta(days=1), 'status': 'paid'},
        {'unit': '804', 'tenant_name': 'Hansa L.', 'amount': Decimal('2600.00'), 'due_date': today + timedelta(days=8), 'paid_date': None, 'status': 'pending'},
        {'unit': '904', 'tenant_name': 'Itthipol N.', 'amount': Decimal('2450.00'), 'due_date': today - timedelta(days=20), 'paid_date': None, 'status': 'overdue'},
        {'unit': '1204', 'tenant_name': 'Jintana W.', 'amount': Decimal('2900.00'), 'due_date': today - timedelta(days=1), 'paid_date': today, 'status': 'paid'},
    ]


def get_seed_monthly_reports():
    return [
        {'title': 'Monthly Operations Report - August 2025', 'month': 8, 'year': 2025},
        {'title': 'Monthly Operations Report - September 2025', 'month': 9, 'year': 2025},
        {'title': 'Monthly Operations Report - October 2025', 'month': 10, 'year': 2025},
        {'title': 'Monthly Operations Report - November 2025', 'month': 11, 'year': 2025},
        {'title': 'Monthly Operations Report - December 2025', 'month': 12, 'year': 2025},
        {'title': 'Monthly Operations Report - January 2026', 'month': 1, 'year': 2026},
        {'title': 'Monthly Operations Report - February 2026', 'month': 2, 'year': 2026},
        {'title': 'Monthly Operations Report - March 2026', 'month': 3, 'year': 2026},
        {'title': 'Monthly Operations Report - April 2026', 'month': 4, 'year': 2026},
        {'title': 'Monthly Operations Report - May 2026', 'month': 5, 'year': 2026},
    ]
