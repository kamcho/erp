"""Seed Grade 9 Cheetah students from fee balances sheet (Excel Academy)."""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Excel.settings")

import django

django.setup()

from django.db import transaction
from django.db.models import Sum
from core.models import School, Grade, Class, Student, StudentProfile

FEMALE_FIRST = {
    "FARAH", "STACEY", "JOY", "LEANNE", "NICE", "ANGEL",
}

ROWS = [
    ("2766", "Farah Abdiazziz", 0),
    ("2969", "Stacey Wanjiku Kamau", 5000),
    ("2973", "Joy Wanjiru Kamau", 0),
    ("2985", "Victor Willies", -30700),
    ("2999", "Riyan Abdulahi", 27500),
    ("3152", "Joy Muthoni Wainaina", 0),
    ("3331", "Leanne Wangari Kimani", 0),
    ("3477", "Brayson Maina", 0),
    ("3556", "Nice Applesent Wambui", 0),
    ("3657", "Tonny Mali Somoni", 0),
    ("3664", "Jayden Matunda", 0),
    ("4063", "Christian Mwangi", 6000),
    ("4114", "Angel Mukami", 16000),
    ("4261", "Abdirizack Hassan", 0),
]

DOB = date(2011, 6, 1)
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
    grade = Grade.objects.filter(name="Grade 9").first()
    klass = Class.objects.filter(school=school, grade=grade, name="Cheetah").first()
    if not school or not klass:
        raise SystemExit("Excel Academy / Grade 9 Cheetah not found")

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
    arrears = StudentProfile.objects.filter(class_id=klass, fee_balance__gt=0).aggregate(s=Sum("fee_balance"))["s"] or 0
    print(f"\nDone. Created {created_n}, updated {updated_n}.")
    print(f"Grade 9 Cheetah total: {total} ({owing} owing, {credit} credit, arrears KES {arrears})")


if __name__ == "__main__":
    run()
