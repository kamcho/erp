"""Seed Grade 7 Tiger students."""
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
    "IRENE", "FAITH", "SHERRY", "ANGEL", "PRECIOUS", "NAJIRA", "TRACY",
    "VELMA", "SHANNEL", "JOY", "DEONNE", "SAMIRA",
}

ROWS = [
    ("008", "IRENE WANJIRU", 5700),
    ("026", "JASON WARARI", 4500),
    ("029", "FAITH GRACIOUS", 0),
    ("038", "KELVIN OTENGO", 0),
    ("052", "SAMSON NJOROGE", 0),
    ("2842", "AIDAN MWANGI MIRIRU", 8000),
    ("2867", "SHERRY NJOKI", 21350),
    ("2883", "SMITH MWANGI", 4800),
    ("2946", "ANGEL WANGECHI MUTITU", -700),
    ("2984", "DELVIN MUNENE", 9300),
    ("3052", "PRECIOUS WAMBUI GITAU", 0),
    ("3214", "NAJIRA ABDIAZIZ", 90200),
    ("3256", "TRACY WAMAITHA KAMAU", 4800),
    ("3258", "VELMA CHEPKEMOI KOECH", 14000),
    ("3271", "SHANNEL MWIHAKI", 18500),
    ("3272", "ERIC JOHN NJUGUNA", 3100),
    ("3273", "ROBERT SAMUEL NJUGUNA", 3100),
    ("3305", "JOY NJERI NDIRANGU", 0),
    ("3447", "DEONNE KAREMBO", 0),
    ("3623", "SAMIRA ALI ADAM", 0),
]

DOB = date(2013, 6, 1)
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
    grade = Grade.objects.filter(name="Grade 7").first()
    klass = Class.objects.filter(school=school, grade=grade, name="Tiger").first()
    if not school or not klass:
        raise SystemExit("Excel Academy / Grade 7 Tiger not found")

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
    print(f"Grade 7 Tiger total: {total} ({owing} owing, {credit} credit)")


if __name__ == "__main__":
    run()
