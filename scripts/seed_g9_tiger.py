"""Seed Grade 9 Tiger students from fee balances sheet (Excel Academy)."""
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
    "ZAWADI", "SARAH", "ASHLEY", "REBECCA", "HOPE", "YVONNE", "TASHA",
    "KIMBERLY", "ERICAH", "AUDREY", "SHARLYN", "NATASHA", "ANGELA",
    "IRENE", "CLARE", "CHLOE",
}

ROWS = [
    ("2746", "Zawadi Zaria", 4500),
    ("2765", "Mohammed Abdiazziz", 0),
    ("2768", "Leon Blessed", 0),
    ("2893", "Eliud Marite", 0),
    ("2895", "Sarah Njambi", 0),
    ("2953", "John Akwata", 0),
    ("2958", "Ethan Ndichu Kamuyu", 12800),
    ("2962", "Ashley Wanjiku Kamande", 4500),
    ("2963", "Rebecca Shanel", 0),
    ("2971", "Jayson Limo Kipchirchir", 0),
    ("2990", "Shawnley Ochoki", 4000),
    ("3251", "Keith Jayden Kihiko", 0),
    ("3442", "Hope Waweru", 21400),
    ("3508", "Ryan Ngucie Muriuki", 0),
    ("3605", "Elvis Otieno Radolo", 0),
    ("3645", "Denzel Kipkurui", 0),
    ("3650", "Yvonne Nikra Wambui", -500),
    ("3686", "Tasha Chelangat", 0),
    ("3788", "Kimberly Bochere Nyamac", 0),
    ("3826", "Ericah Nowell Ayuma", 0),
    ("3828", "Sammy Murengi Mwangi", 0),
    ("3842", "Audrey Wangari Oisebe", 0),
    ("3857", "Sharlyn Wanjiku Matimu", 0),
    ("3861", "Natasha Wamuyu", 12500),
    ("3896", "Angela Masika", 5050),
    ("3902", "Irene Waithira Irungu", -5500),
    ("3909", "Clare Waithira Mutitu", 4500),
    ("4031", "Martin Chege Wambui", 0),
    ("4137", "Moses Baraka", 3000),
    ("4175", "Chloe Wanjiru", 1000),
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
    klass = Class.objects.filter(school=school, grade=grade, name="Tiger").first()
    if not school or not klass:
        raise SystemExit("Excel Academy / Grade 9 Tiger not found")

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
    print(f"Grade 9 Tiger total: {total} ({owing} owing, {credit} credit, arrears KES {arrears})")


if __name__ == "__main__":
    run()
