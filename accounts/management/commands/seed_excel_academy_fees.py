from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import FeeStructure, AdditionalCharges, AdmissionFee, AuxiliaryServiceType
from core.models import School, Grade, Term


class Command(BaseCommand):
    help = "Seed Excel Academy fee structures from the official fee sheet."

    # Term name -> amount (KES)
    DAY_TIERS = [
        {
            "name": "ECDE (Playgroup, PP1, PP2)",
            "grades": ["Play Group", "PP1", "PP2"],
            "amounts": {"Term 1": 10700, "Term 2": 10000, "Term 3": 10000},
        },
        {
            "name": "Grade 1-3",
            "grades": ["Grade 1", "Grade 2", "Grade 3"],
            "amounts": {"Term 1": 15700, "Term 2": 15000, "Term 3": 15000},
        },
        {
            "name": "Grade 4-6",
            "grades": ["Grade 4", "Grade 5", "Grade 6"],
            "amounts": {"Term 1": 16700, "Term 2": 16000, "Term 3": 16000},
        },
        {
            "name": "Grade 7 (Day Scholar)",
            "grades": ["Grade 7"],
            "amounts": {"Term 1": 20000, "Term 2": 20000, "Term 3": 20000},
        },
        {
            "name": "Grade 8 (Day Scholar)",
            "grades": ["Grade 8"],
            "amounts": {"Term 1": 20000, "Term 2": 20000, "Term 3": 20000},
        },
        {
            "name": "Grade 9 (Day Scholar)",
            "grades": ["Grade 9"],
            "amounts": {"Term 1": 23000, "Term 2": 23000, "Term 3": 23000},
        },
    ]

    BOARDING_AMOUNT = Decimal("25000.00")
    ADMISSION_AMOUNT = Decimal("5000.00")

    def handle(self, *args, **options):
        school = School.objects.filter(name__iexact="Excel Academy").first()
        if not school:
            self.stderr.write(self.style.ERROR("Excel Academy school not found."))
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
                self.stdout.write(f"Seeding day scholar fees for {term_name}...")
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

                self.stdout.write(f"Seeding boarding fee for {term_name}...")
                fs_boarder, created = FeeStructure.objects.get_or_create(
                    school=school,
                    term=term,
                    student_type="boarder",
                    name="Boarding Fee",
                    defaults={"amount": self.BOARDING_AMOUNT},
                )
                fs_boarder.amount = self.BOARDING_AMOUNT
                fs_boarder.grade.set(Grade.objects.all())
                fs_boarder.save()
                seeded_ids.add(fs_boarder.id)
                action = "Created" if created else "Updated"
                self.stdout.write(f"  {action}: Boarding Fee = {self.BOARDING_AMOUNT}")

            # Drop obsolete Academy fee rows not in this sheet
            obsolete = FeeStructure.objects.filter(school=school).exclude(id__in=seeded_ids)
            if obsolete.exists():
                count = obsolete.count()
                obsolete.delete()
                self.stdout.write(self.style.WARNING(f"Removed {count} obsolete fee structure(s)."))

            junior = Grade.objects.filter(name__in=["Grade 7", "Grade 8", "Grade 9"])

            lab, _ = AdditionalCharges.objects.get_or_create(
                school=school,
                name="Laboratory/Technical Materials",
                defaults={"amount": Decimal("3000.00")},
            )
            lab.amount = Decimal("3000.00")
            lab.term = None  # all terms
            lab.grades.set(junior)
            lab.save()
            self.stdout.write("Additional charge: Laboratory/Technical Materials = 3000 (G7-9)")

            cbc, _ = AdditionalCharges.objects.get_or_create(
                school=school,
                name="CBC Materials/Services",
                defaults={"amount": Decimal("1500.00")},
            )
            cbc.amount = Decimal("1500.00")
            cbc.term = None
            cbc.grades.set(junior)
            cbc.save()
            self.stdout.write("Additional charge: CBC Materials/Services = 1500 (G7-9)")

            # Remediials as auxiliary service types (opt-in / bulk invoice)
            rem_lower_grades = Grade.objects.filter(
                name__in=["PP1", "PP2", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"]
            )
            rem_upper_grades = Grade.objects.filter(
                name__in=["Grade 6", "Grade 7", "Grade 8", "Grade 9"]
            )

            rem_lower, _ = AuxiliaryServiceType.objects.get_or_create(
                school=school,
                name="Remedial (PP1 - Grade 5)",
                defaults={
                    "amount": Decimal("1000.00"),
                    "description": "Termly remedial classes for PP1 to Grade 5",
                    "is_active": True,
                },
            )
            rem_lower.amount = Decimal("1000.00")
            rem_lower.description = "Termly remedial classes for PP1 to Grade 5"
            rem_lower.is_active = True
            rem_lower.save()
            rem_lower.grades.set(rem_lower_grades)
            self.stdout.write("Auxiliary: Remedial (PP1 - Grade 5) = 1000")

            rem_upper, _ = AuxiliaryServiceType.objects.get_or_create(
                school=school,
                name="Remedial (Grade 6 - Grade 9)",
                defaults={
                    "amount": Decimal("1500.00"),
                    "description": "Termly remedial classes for Grade 6 to Grade 9",
                    "is_active": True,
                },
            )
            rem_upper.amount = Decimal("1500.00")
            rem_upper.description = "Termly remedial classes for Grade 6 to Grade 9"
            rem_upper.is_active = True
            rem_upper.save()
            rem_upper.grades.set(rem_upper_grades)
            self.stdout.write("Auxiliary: Remedial (Grade 6 - Grade 9) = 1500")

            AdmissionFee.objects.all().delete()
            AdmissionFee.objects.create(amount=self.ADMISSION_AMOUNT)
            self.stdout.write(f"Admission fee = {self.ADMISSION_AMOUNT} (new pupils, once)")

        self.stdout.write(
            self.style.SUCCESS(
                f"Fee sheet seeded for {school.name}. "
                "Transport (4,800-7,200) is set per route in Transport — not seeded here."
            )
        )
