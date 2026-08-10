from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import FeeStructure, AdditionalCharges
from core.models import School, Grade, Term


class Command(BaseCommand):
    help = "Seed Excel Woodlands fee structures from the official fee sheet."

    DAY_TIERS = [
        {
            "name": "ECDE (Playgroup, PP1, PP2)",
            "grades": ["Play Group", "PP1", "PP2"],
            "amounts": {"Term 1": 10700, "Term 2": 9500, "Term 3": 8000},
        },
        {
            "name": "Grade 1-3",
            "grades": ["Grade 1", "Grade 2", "Grade 3"],
            "amounts": {"Term 1": 15700, "Term 2": 14500, "Term 3": 11500},
        },
        {
            "name": "Grade 4-6",
            "grades": ["Grade 4", "Grade 5", "Grade 6"],
            "amounts": {"Term 1": 16700, "Term 2": 15000, "Term 3": 12500},
        },
        {
            "name": "Junior Secondary (Grade 7)",
            "grades": ["Grade 7"],
            "amounts": {"Term 1": 19500, "Term 2": 17000, "Term 3": 15000},
        },
        {
            "name": "Junior Secondary (Grade 8)",
            "grades": ["Grade 8"],
            "amounts": {"Term 1": 19500, "Term 2": 17000, "Term 3": 15000},
        },
        {
            "name": "Junior Secondary (Grade 9)",
            "grades": ["Grade 9"],
            "amounts": {"Term 1": 19500, "Term 2": 17000, "Term 3": 15000},
        },
    ]

    ADMISSION_AMOUNT = Decimal("3000.00")

    def handle(self, *args, **options):
        school, _ = School.objects.get_or_create(
            name="Excel Woodlands",
            defaults={
                "address": "P.O BOX 9609-20100, NAKURU",
                "phone": "0724857890",
                "email": "woodlands@excelschools.com",
            },
        )
        school.address = "P.O BOX 9609-20100, NAKURU"
        school.phone = "0724857890"
        school.email = school.email or "woodlands@excelschools.com"
        school.save(update_fields=["address", "phone", "email"])
        self.stdout.write("School contacts: 0724857890 / 0708333545 (stored primary 0724857890)")

        terms = {
            "Term 1": Term.objects.filter(name__iexact="Term 1").first(),
            "Term 2": Term.objects.filter(name__iexact="Term 2").first(),
            "Term 3": Term.objects.filter(name__iexact="Term 3").first(),
        }
        missing = [name for name, obj in terms.items() if obj is None]
        if missing:
            self.stderr.write(self.style.ERROR(f"Missing terms: {', '.join(missing)}"))
            return

        with transaction.atomic():
            seeded_ids = set()

            for term_name, term in terms.items():
                self.stdout.write(f"Seeding Woodlands day fees for {term_name}...")
                for tier in self.DAY_TIERS:
                    grades = Grade.objects.filter(name__in=tier["grades"])
                    if grades.count() != len(tier["grades"]):
                        found = list(grades.values_list("name", flat=True))
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Grades missing for {tier['name']}: "
                                f"wanted {tier['grades']}, found {found}"
                            )
                        )
                    amount = Decimal(tier["amounts"][term_name])
                    fs, created = FeeStructure.objects.get_or_create(
                        school=school,
                        term=term,
                        student_type="day",
                        name=tier["name"],
                        defaults={"amount": amount},
                    )
                    fs.amount = amount
                    fs.grade.set(grades)
                    fs.save()
                    seeded_ids.add(fs.id)
                    action = "Created" if created else "Updated"
                    self.stdout.write(f"  {action}: {tier['name']} = {amount}")

            obsolete = FeeStructure.objects.filter(school=school).exclude(id__in=seeded_ids)
            if obsolete.exists():
                count = obsolete.count()
                obsolete.delete()
                self.stdout.write(self.style.WARNING(f"Removed {count} obsolete fee structure(s)."))

            # School-scoped admission (AdmissionFee model is global / Academy).
            admission, _ = AdditionalCharges.objects.get_or_create(
                school=school,
                name="Admission Fee",
                defaults={"amount": self.ADMISSION_AMOUNT},
            )
            admission.amount = self.ADMISSION_AMOUNT
            admission.term = None
            admission.grades.set(Grade.objects.all())
            admission.save()
            self.stdout.write(f"Additional charge: Admission Fee = {self.ADMISSION_AMOUNT} (once)")

        self.stdout.write(
            self.style.SUCCESS(
                f"Fee sheet seeded for {school.name}. "
                "Transport (3,500-5,000) is set per route in Transport — not seeded here."
            )
        )
