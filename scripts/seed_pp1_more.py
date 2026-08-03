"""Add remaining PP1 students from fee sheet. Skip adm 4094."""
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
    "VELMA", "LIANA", "PRECIOUS", "ESTHER", "TERESIA", "ARRIANA", "VIVIAN",
    "BRIANNA", "ERICA", "ELSIE", "BRIANA",
}

ROWS = [
    ("4071", "CRISTON WRIGHT SAMBA", 0),
    ("4074", "NORLAN MICHAEL OUKO", 0),
    ("4077", "VELMA KINSLEY", 0),
    ("4082", "AUSTIN MBUTHIA NDERITU", 0),
    ("4086", "LIANA JERUTO KURUI", 0),
    ("4093", "PRECIOUS WAMBUI MACHARIA", 0),
    # 4094 skipped — no longer in system
    ("4122", "TERESIA NJERI", 0),
    ("4130", "ARRIANA WANJIRU", 0),
    ("4134", "VIVIAN SHERRY", 0),
    ("4139", "BRIANNA CHEROP", 0),
    ("4140", "CARL KIPKOECH", 0),
    ("4167", "ERICA NYAMBURA MAINA", 0),
    ("4194", "DAYTON ELDAD JAMARI", 0),
    ("4200", "ELSIE MEGHAN KAMUNGU", 0),
    ("4250", "BRIANA MUMBI", 9200),
]

DOB = date(2021, 6, 1)
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
    grade = Grade.objects.filter(name="PP1").first()
    klass = Class.objects.filter(school=school, grade=grade, name="PP1").first()
    if not school or not klass:
        raise SystemExit("Excel Academy / PP1 class not found")

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
    print(f"\nDone. Created {created_n}, updated {updated_n}. PP1 total now: {total}")
    print("Skipped 4094 Esther Muthoni Pg Wanjiri as requested.")


if __name__ == "__main__":
    run()
