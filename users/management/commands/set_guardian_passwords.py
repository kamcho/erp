from django.core.management.base import BaseCommand
from users.models import MyUser


class Command(BaseCommand):
    help = "Set each Guardian's password to their phone number (skips blank phones)."

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Count guardians that would be updated without saving.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        qs = (
            MyUser.objects.filter(role='Guardian')
            .exclude(phone_number__isnull=True)
            .exclude(phone_number='')
        )
        total = qs.count()
        updated = 0
        for guardian in qs.iterator():
            phone = (guardian.phone_number or '').strip()
            if not phone:
                continue
            if dry_run:
                updated += 1
                continue
            guardian.set_password(phone)
            guardian.save(update_fields=['password'])
            updated += 1

        action = 'Would update' if dry_run else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} {updated} of {total} guardians with phone numbers.'))
