from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import AdditionalCharges, FeeStructure
from core.models import Grade, School, Term

SCHOOL_NAME = "Excel Grassland"

# Same amount for Term 1, 2, and 3 unless the fee sheet specifies otherwise.
DAY_TIERS = [
    {
        "name": "ECDE (Play Group, PP1, PP2)",
        "grades": ["Play Group", "PP1", "PP2"],
        "amount": Decimal("8500.00"),
    },
    {
        "name": "Grade 1-3",
        "grades": ["Grade 1", "Grade 2", "Grade 3"],
        "amount": Decimal("13000.00"),
    },
    {
        "name": "Grade 4-6",
        "grades": ["Grade 4", "Grade 5", "Grade 6"],
        "amount": Decimal("14500.00"),
    },
    {
        "name": "Grade 7-9",
        "grades": ["Grade 7", "Grade 8", "Grade 9"],
        "amount": Decimal("19500.00"),
    },
]

BOARDER_TIERS = [
    {
        "name": "Boarding (Grade 3-6)",
        "grades": ["Grade 3", "Grade 4", "Grade 5", "Grade 6"],
        "amount": Decimal("20000.00"),
    },
    {
        "name": "Boarding (Grade 7-9)",
        "grades": ["Grade 7", "Grade 8", "Grade 9"],
        "amount": Decimal("25000.00"),
    },
]

ADMISSION_AMOUNT = Decimal("2000.00")


class Command(BaseCommand):
    help = "Seed Excel Grassland fee structures from the official fee sheet."

    def handle(self, *args, **options):
        school = School.objects.filter(name__iexact=SCHOOL_NAME).first()
        if not school:
            self.stderr.write(self.style.ERROR(f"{SCHOOL_NAME} school not found. Run sync_excel_grassland_classes first."))
            return

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
                self.stdout.write(f"Seeding Grassland day fees for {term_name}...")
                for tier in DAY_TIERS:
                    grades = Grade.objects.filter(name__in=tier["grades"])
                    if grades.count() != len(tier["grades"]):
                        found = list(grades.values_list("name", flat=True))
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Grades missing for {tier['name']}: "
                                f"wanted {tier['grades']}, found {found}"
                            )
                        )

                    fs, created = FeeStructure.objects.get_or_create(
                        school=school,
                        term=term,
                        student_type="day",
                        name=tier["name"],
                        defaults={"amount": tier["amount"]},
                    )
                    fs.amount = tier["amount"]
                    fs.grade.set(grades)
                    fs.save()
                    seeded_ids.add(fs.id)
                    action = "Created" if created else "Updated"
                    self.stdout.write(f"  {action}: {tier['name']} (day) = {tier['amount']}")

                self.stdout.write(f"Seeding Grassland boarding fees for {term_name}...")
                for tier in BOARDER_TIERS:
                    grades = Grade.objects.filter(name__in=tier["grades"])
                    if grades.count() != len(tier["grades"]):
                        found = list(grades.values_list("name", flat=True))
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Grades missing for {tier['name']}: "
                                f"wanted {tier['grades']}, found {found}"
                            )
                        )

                    fs, created = FeeStructure.objects.get_or_create(
                        school=school,
                        term=term,
                        student_type="boarder",
                        name=tier["name"],
                        defaults={"amount": tier["amount"]},
                    )
                    fs.amount = tier["amount"]
                    fs.grade.set(grades)
                    fs.save()
                    seeded_ids.add(fs.id)
                    action = "Created" if created else "Updated"
                    self.stdout.write(f"  {action}: {tier['name']} (boarder) = {tier['amount']}")

            obsolete = FeeStructure.objects.filter(school=school).exclude(id__in=seeded_ids)
            if obsolete.exists():
                count = obsolete.count()
                obsolete.delete()
                self.stdout.write(self.style.WARNING(f"Removed {count} obsolete fee structure(s)."))

            admission, _ = AdditionalCharges.objects.get_or_create(
                school=school,
                name="Admission Fee",
                defaults={"amount": ADMISSION_AMOUNT},
            )
            admission.amount = ADMISSION_AMOUNT
            admission.term = None
            admission.grades.set(Grade.objects.all())
            admission.save()
            self.stdout.write(f"Additional charge: Admission Fee = {ADMISSION_AMOUNT} (once)")

        self.stdout.write(
            self.style.SUCCESS(
                f"Fee sheet seeded for {school.name}. "
                "Day: PG-PP2 8,500 | G1-3 13,000 | G4-6 14,500 | G7-9 19,500. "
                "Boarding: G3-6 20,000 | G7-9 25,000."
            )
        )
