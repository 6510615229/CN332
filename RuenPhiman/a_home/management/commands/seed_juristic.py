from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from a_home.mock_juristic import (
    get_seed_billing_invoices,
    get_seed_maintenance_requests,
    get_seed_monthly_reports,
)
from a_home.models import BillingInvoice, MaintenanceRequest, MonthlyReport
from a_users.models import Profile


class Command(BaseCommand):
    help = 'Seed sample maintenance, billing, and monthly report records for the Juristic role.'

    def handle(self, *args, **options):
        User = get_user_model()
        resident, _ = User.objects.get_or_create(
            username='sample_resident',
            defaults={'email': 'sample_resident@example.com'},
        )
        Profile.objects.get_or_create(user=resident, defaults={'role': 'resident'})

        juristic, _ = User.objects.get_or_create(
            username='sample_juristic',
            defaults={'email': 'sample_juristic@example.com', 'is_staff': True},
        )
        Profile.objects.get_or_create(user=juristic, defaults={'role': 'juristic'})

        maintenance_created = 0
        for request_data in get_seed_maintenance_requests():
            _, created = MaintenanceRequest.objects.get_or_create(
                title=request_data['title'],
                defaults={
                    **request_data,
                    'resident': resident,
                },
            )
            if created:
                maintenance_created += 1

        billing_created = 0
        for invoice_data in get_seed_billing_invoices():
            _, created = BillingInvoice.objects.get_or_create(
                unit=invoice_data['unit'],
                due_date=invoice_data['due_date'],
                defaults={
                    **invoice_data,
                    'resident': resident,
                },
            )
            if created:
                billing_created += 1

        reports_created = 0
        for report_data in get_seed_monthly_reports():
            report, created = MonthlyReport.objects.get_or_create(
                month=report_data['month'],
                year=report_data['year'],
                defaults={
                    'title': report_data['title'],
                    'uploaded_by': juristic,
                },
            )
            if created:
                filename = f"monthly-report-{report_data['year']}-{report_data['month']:02d}.txt"
                content = ContentFile(
                    f"{report_data['title']}\n\nSample monthly report content for demo purposes.\n".encode('utf-8')
                )
                report.file.save(filename, content, save=True)
                reports_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Created {maintenance_created} maintenance request(s), '
                f'{billing_created} billing invoice(s), and {reports_created} monthly report(s).'
            )
        )
