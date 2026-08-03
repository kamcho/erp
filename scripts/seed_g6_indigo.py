"""Re-seed Grade 6 Indigo students."""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Excel.settings")

import django

django.setup()

from django.db import transaction
from core.models import School, Grade, Class, Student, StudentProfile

FEMALE_FIRST = {
    "ATTIA", "TRIZAH", "SUBIRA", "BRIDGET", "MERCY", "RAHMA", "HASBAY",
    "KAITLINE", "LOVELYNE", "AMAYA", "SHALOM", "MUNIRA", "SASHA", "TERESA",
    "UMULKHEIR", "LYNN",
}

ROWS = [
    ("3470", "ATTIA MUTHONI", 0),
    ("3475", "TRIZAH WATHITHI", 0),
    ("3480", "SUBIRA WANJIKU", 4800),
    ("3487", "BRIDGET NYOKABI ITEGI", 0),
    ("3493", "MERCY MUTHONI WOKABI", 6400),
    ("3494", "RAHMA HUSSEIN", 15100),
    ("3498", "GEORGE MURAGURI", 0),
    ("3514", "HASBAY NAYA", 8700),
    ("3516", "JUBAL LYSANIAS", 100),
    ("3716", "KAITLINE ELIANA", 0),
    ("3761", "WAYNE WILSHERE RICHARD", 0),
    ("3765", "LOVELYNE WANGARI MWAUR", 4800),
    ("3786", "AMAYA WANJIRU", 0),
    ("3797", "SHALOM NJERI IKENYE", -5400),
    ("3836", "SAMUEL GITONGA MIRUGI", 0),
    ("3851", "MUNIRA ALINOOR IBRAHIM", 4100),
    ("4072", "SASHA SARA KEJI", 5000),
    ("4102", "TERESA WANJIRU", 0),
    ("4124", "UMULKHEIR JIBRIL", 0),
    ("4240", "LYNN NJOKI ITAMBU", 0),
]

DOB = date(2014, 6, 1)
JOINED = date(2026, 1, 5)


def split_name(full: str):
    parts = [p for p in full.strip().split() if p]
    if len(parts) == 1:
        return parts[0].title(), "", parts[0].title()
    if len(parts) == 2:
        return parts[0].title(), "", parts[1].title()
    return parts[0].title(), " ".join(parts[1:-1]).title(), parts[-1].title()


def run():
    school = School.objects.filter(name__iexact="Excel Academy").first()
    grade = Grade.objects.filter(name="Grade 6").first()
    klass = Class.objects.filter(school=school, grade=grade, name="Indigo").first()
    if not school or not klass:
        raise SystemExit("Excel Academy / Grade 6 Indigo not found")

    created_n = updated_n = 0
    with transaction.atomic():
        for adm, name, bal in ROWS:
            first, middle, last = split_name(name)
            gender = "female" if first.upper() in FEMALE_FIRST else "male"
            student = Student.objects.filter(adm_no=str(adm)).first()
            if not student:
                student = Student(
                    adm_no=str(adm),
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
                updated_n += 1
                tag = "Updated"
            student.save()

            profile, _ = StudentProfile.objects.get_or_create(
                student=student,
                defaults={
                    "school": school,
                    "class_id": klass,
                    "fee_balance": bal,
                    "status": "Active",
                    "discipline": 100,
                },
            )
            profile.school = school
            profile.class_id = klass
            profile.fee_balance = bal
            profile.status = "Active"
            profile.save()
            print(f"  {tag}: {adm} {student.get_full_name()} balance={profile.fee_balance}")

    total = StudentProfile.objects.filter(class_id=klass).count()
    owing = StudentProfile.objects.filter(class_id=klass, fee_balance__gt=0).count()
    credit = StudentProfile.objects.filter(class_id=klass, fee_balance__lt=0).count()
    print(f"\nDone. Created {created_n}, updated {updated_n}.")
    print(f"Grade 6 Indigo total: {total} ({owing} owing, {credit} credit)")


if __name__ == "__main__":
    run()
