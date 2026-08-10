"""Seed Excel Woodlands Play Group students from Term 2 2026 fee sheet.

ADM column on the sheet is admission fee (not admission number).
Admission numbers are left blank for later assignment.
"""
import os
import sys
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Excel.settings")

import django

django.setup()

from django.db import transaction
from django.db.models import Q
from core.models import School, Grade, Class, Student, StudentProfile

FEMALE_FIRST = {
    "TIFFANY", "KARRYN", "MAKYLA", "VALENTINE", "SHANAH", "FAITH",
    "FAUSTINA", "EPIPHANY", "ZAYLA", "MILA", "ADRIANA",
}

# name, fee_balance (sheet BALANCE; Faith overpayment corrected to negative)
ROWS = [
    ("Tiffany Wanjiru", 0),
    ("Bobby Oliver", 0),
    ("Karryn Wanjugu", 0),
    ("Aiden Elden", 0),
    ("Carson Myles", 0),
    ("Makyla Njeri", 2500),
    ("Derran Muigai", 3000),
    ("Kenan Kind", 0),
    ("Valentine Liz", 0),
    ("Seastone Kariuki", 0),
    ("Asher Maina", 3500),
    ("Nirrel Christian", 0),
    ("Shanah Wambui", 5850),
    ("Kaynan Junior", 0),
    ("Aidan Kimani", 0),
    ("Brian Thuo", 0),
    # Sheet shows +1000 but paid 13500 on total 12500 → overpayment
    ("Faith Njeri", -1000),
    ("Ivan Baraka", 0),
    ("Faustina Njeri", 0),
    ("Dylan Ivan", 0),
    ("Epiphany Kabatha", 0),
    ("Gavriel Vyson", 0),
    ("Zayla Wambui", 0),
    ("Mila Kaysha", 0),
    ("Adriana Wairimu", 0),
]

DOB = date(2022, 1, 1)
JOINED = date(2026, 1, 5)


def split_name(full: str):
    parts = [p for p in full.strip().split() if p]
    if len(parts) == 1:
        return parts[0].title(), "", parts[0].title()
    if len(parts) == 2:
        return parts[0].title(), "", parts[1].title()
    return parts[0].title(), " ".join(parts[1:-1]).title(), parts[-1].title()


def run():
    school = School.objects.filter(name__iexact="Excel Woodlands").first()
    grade = Grade.objects.filter(name="Play Group").first()
    klass = Class.objects.filter(school=school, grade=grade, name__iexact="Play Group").first()
    if not school or not klass:
        raise SystemExit("Excel Woodlands / Play Group not found — create class first (ask permission).")

    created_n = updated_n = 0
    with transaction.atomic():
        for name, bal in ROWS:
            first, middle, last = split_name(name)
            gender = "female" if first.upper() in FEMALE_FIRST else "male"

            # Match existing blank-adm Woodlands Play Group learner by name
                student = Student.objects.filter(
                    first_name__iexact=first,
                    last_name__iexact=last,
                    studentprofile__school=school,
                    studentprofile__class_id=klass,
                ).filter(Q(adm_no__isnull=True) | Q(adm_no="")).first()
            if not student:
                student = Student(
                    adm_no=None,
                    first_name=first,
                    middle_name=middle,
                    last_name=last,
                    date_of_birth=DOB,
                    joined_date=JOINED,
                    gender=gender,
                    fee_category="day",
                    is_boarder=False,
                )
                created_n += 1
                tag = "Created"
            else:
                student.first_name = first
                student.middle_name = middle
                student.last_name = last
                student.gender = gender
                student.fee_category = "day"
                student.is_boarder = False
                updated_n += 1
                tag = "Updated"
            student.save()

            profile, _ = StudentProfile.objects.get_or_create(
                student=student,
                defaults={
                    "school": school,
                    "class_id": klass,
                    "fee_balance": Decimal(bal),
                    "status": "Active",
                    "discipline": 100,
                },
            )
            profile.school = school
            profile.class_id = klass
            profile.fee_balance = Decimal(bal)
            profile.status = "Active"
            profile.save()
            print(f"  {tag}: (no adm) {student.get_full_name()} balance={profile.fee_balance}")

    total = StudentProfile.objects.filter(class_id=klass).count()
    print(f"\nDone. Created {created_n}, updated {updated_n}.")
    print(f"Excel Woodlands Play Group total: {total}")


if __name__ == "__main__":
    run()
