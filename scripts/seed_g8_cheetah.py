"""Seed Grade 8 Cheetah students from fee balances sheet (Excel Academy)."""
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
    "WHITNEY", "WINNIE", "ALEXIS", "SALMA", "LIBERTY", "SAMANTHA", "SASHA",
    "EVA", "JOY", "TAMARA", "WANDA", "BUSHRA", "PRISCAH",
}

ROWS = [
    ("2777", "Marcus Njuguna", 13500),
    ("2804", "Marwa Abdiaziz", 27100),
    ("2861", "Owen Kipchirchir", 125700),
    ("3000", "Samuel Obungo", 18210),
    ("3093", "Steve Gerald Muhatia", 8000),
    ("3105", "Whitney Sintamei", 45200),
    ("3128", "Winnie Wanjiku Mbai", 2000),
    ("3142", "Ethan Nyenjeri", 0),
    ("3147", "Alexis Chepkemoi", 0),
    ("3157", "Melvin Mwangi", 23500),
    ("3158", "Harrison Nga'nga'", 0),
    ("3170", "Salma Mohammed", 0),
    ("3204", "Liberty Bright", -500),
    ("3315", "Samantha Milka Asaka", 0),
    ("3402", "Sasha Nyambogo", 7500),
    ("3424", "Steve Njugi", 0),
    ("3509", "Reu Mburu Kamau", 7000),
    ("3529", "Joseph Mulinge", -500),
    ("3668", "Eva Wambui Mwangi", -29300),
    ("3689", "Joy Njeri Njoroge", 0),
    ("3710", "Leon Luther Wainaina", 0),
    ("3718", "Tamara Alice Wanjiru", 2400),
    ("4027", "Alvan Kariuki Muthoni", 9500),
    ("4042", "Mohamed Abdirahman Has", 3000),
    ("4062", "Wanda Wanja", 0),
    ("4100", "Bushra Ibrahim", 2500),
    ("4113", "Adrian Kamau", 9000),
    ("4170", "Nigel Chai Lewa", 0),
    ("4193", "Dylan Muriithi Kibaara", 0),
    ("4201", "Priscah Kemunto", 9000),
    ("4228", "Sean Trevor Rono", 9500),
    ("4260", "Akram Abdisalam", 0),
]

DOB = date(2012, 6, 1)
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
    grade = Grade.objects.filter(name="Grade 8").first()
    klass = Class.objects.filter(school=school, grade=grade, name="Cheetah").first()
    if not school or not klass:
        raise SystemExit("Excel Academy / Grade 8 Cheetah not found")

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
    print(f"Grade 8 Cheetah total: {total} ({owing} owing, {credit} credit, arrears KES {arrears})")


if __name__ == "__main__":
    run()
