"""
Seed Play Group + PP1 students from fee balances sheet (Term 2 2026).
Outstanding Bal. -> StudentProfile.fee_balance
  +ve = amount owed, 0 = clear, -ve = overpayment/credit
"""
import os
import sys
from datetime import date
from decimal import Decimal, InvalidOperation

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Excel.settings")

import django

django.setup()

from django.db import transaction

from core.models import School, Grade, Class, Student, StudentProfile

FEMALE_FIRST = {
    "DAMIELLA", "TIANA", "FLORENCE", "LESLEY", "PEACE", "ROSHNI", "TASHA",
    "FAVOUR", "EVE", "KELLY", "ASHLYN", "ZAIRA", "TALIA", "DAISY", "BLESSING",
    "IMMACULATE", "JASMINE", "WANGUI", "MELISSA", "IMANI", "PENELOPE", "ZUENA",
    "FRANCICA", "TINSLEE", "ANGELLIZ", "MILAN",
}

STUDENTS = {
    "Play Group": [
        ("4115", "EDWIN MAGUSA ONSERIO", -4250),
        ("4136", "TRAVIS AYUNGA NYAMACHE", 0),
        ("4147", "DAMIELLA NYANCHAMA BOGI", 0),
        ("4148", "ADRIAN LUCIUS KINYUA", 0),
        ("4153", "HUMPHREY NGUGI", 0),
        ("4166", "MILAN WAMBUI MURIITHI", 0),
        ("4182", "TIANA SKYE", 0),
        ("4186", "ADRIAN MUCHIRI MAINA", 0),
        ("4187", "FLORENCE IVANKA", 0),
        ("4191", "AZIEL BARASA MUTAMBO", 0),
        ("4196", "LESLEY JENAH WANJIRU", 0),
        ("4197", "PEACE MURIMI MUTUGI", 0),
        ("4202", "ROSHNI CHELANGAT CHIRCHIF", 0),
        ("4203", "FAHAD KADIWA", 0),
        ("4211", "TASHA GIFT WAKIO", 0),
        ("4218", "WISDOM NGURE KURIA", 0),
        ("4222", "FAVOUR KOIRA", 7650),
        ("4229", "EVE WAMITHA MUIGAI", 7600),
        ("4233", "KELLY WANGUI", 0),
        ("4236", "ASHLYN JADE MUTHAMA", 0),
        ("4237", "ZAIRA ZAWADI WANJIRU", 0),
        ("4238", "RYAN KIPCHUMBA", 500),
        ("4241", "TALIA WANJIRU NJERI", 0),
        ("4245", "CHRISANT JOSEPH DWALLOW", 7500),
        ("4246", "LEON MURIITHI KAGICHU", -200),
        ("4249", "BLESSING NYAWIRA GITAU", 0),
        ("4252", "TROY MUCHIRI MUIGAI", 17800),
        ("4254", "DAISY KEMUNTO SEREMBE", 0),
    ],
    "PP1": [
        ("3876", "IMMACULATE WAMBUI GACHI", 0),
        ("3955", "JASMINE WAMBUI NDEGWA", 0),
        ("3977", "WANGUI MUTHONI NDIRITU", 0),
        ("3978", "MELISSA NYANDURU", -1100),
        ("3979", "ADAM MYLES MUNYWOKI", 2000),
        ("3982", "ZANE CHEGE", 5000),
        ("3985", "BRIGHTON SHUTHO", 6200),
        ("3994", "IMANI GWEN NYAMBURA", 9000),
        ("4000", "RICHARD RAYMOND MYLES", 0),
        ("4016", "DANILO KORI KAGWANJA", 0),
        ("4038", "PENELOPE ALYA WANJIKU", 2500),
        ("4046", "ZUENA MAKENA", 0),
        ("4054", "FRANCICA ADAOMA", 0),
        ("4056", "RONAN MAINA", 0),
        ("4058", "TINSLEE WAMBUI KARI", 0),
        ("4067", "ANGELLIZ WAMBUI NGUMI", 14800),
        ("4069", "JABALI NAOL", 14700),
    ],
}

DOB_BY_GRADE = {
    "Play Group": date(2022, 6, 1),
    "PP1": date(2021, 6, 1),
}
JOINED = date(2026, 1, 5)


def split_name(full: str) -> tuple[str, str, str]:
    parts = [p for p in full.strip().split() if p]
    if not parts:
        return "Unknown", "", "Unknown"
    if len(parts) == 1:
        return parts[0].title(), "", parts[0].title()
    if len(parts) == 2:
        return parts[0].title(), "", parts[1].title()
    return parts[0].title(), " ".join(parts[1:-1]).title(), parts[-1].title()


def guess_gender(first: str) -> str:
    return "female" if first.upper() in FEMALE_FIRST else "male"


def upsert_student(school, klass, adm_no: str, full_name: str, balance: int, dob: date):
    first, middle, last = split_name(full_name)
    gender = guess_gender(first)

    student = Student.objects.filter(adm_no=str(adm_no)).first()
    created = False
    if not student:
        student = Student(
            adm_no=str(adm_no),
            first_name=first,
            middle_name=middle,
            last_name=last,
            date_of_birth=dob,
            joined_date=JOINED,
            gender=gender,
            fee_category="day",
            is_boarder=False,
        )
        created = True
    else:
        student.first_name = first
        student.middle_name = middle
        student.last_name = last
        student.gender = gender

    student.save()

    profile, _ = StudentProfile.objects.get_or_create(
        student=student,
        defaults={
            "school": school,
            "class_id": klass,
            "fee_balance": balance,
            "status": "Active",
            "discipline": 100,
        },
    )
    profile.school = school
    profile.class_id = klass
    profile.fee_balance = balance
    profile.status = "Active"
    profile.save()

    return created, student, profile


def run():
    school = School.objects.filter(name__iexact="Excel Academy").first()
    if not school:
        raise SystemExit("Excel Academy not found")

    created_n = updated_n = 0
    with transaction.atomic():
        for grade_name, rows in STUDENTS.items():
            grade = Grade.objects.filter(name=grade_name).first()
            if not grade:
                raise SystemExit(f"Grade missing: {grade_name}")
            klass = Class.objects.filter(school=school, grade=grade, name=grade_name).first()
            if not klass:
                klass = Class.objects.filter(school=school, grade=grade).first()
            if not klass:
                raise SystemExit(f"Class missing for {grade_name}")

            dob = DOB_BY_GRADE[grade_name]
            print(f"\n{grade_name} -> class id={klass.id} ({klass.name})")
            for adm, name, bal in rows:
                created, student, profile = upsert_student(
                    school, klass, adm, name, int(bal), dob
                )
                if created:
                    created_n += 1
                    tag = "Created"
                else:
                    updated_n += 1
                    tag = "Updated"
                print(
                    f"  {tag}: {student.adm_no} {student.get_full_name()} "
                    f"balance={profile.fee_balance}"
                )

    print(f"\nDone. Created {created_n}, updated {updated_n}.")
    for grade_name in STUDENTS:
        klass = Class.objects.filter(
            school=school, grade__name=grade_name, name=grade_name
        ).first()
        n = StudentProfile.objects.filter(class_id=klass).count()
        owing = StudentProfile.objects.filter(class_id=klass, fee_balance__gt=0).count()
        credit = StudentProfile.objects.filter(class_id=klass, fee_balance__lt=0).count()
        print(f"  {grade_name}: {n} students ({owing} owing, {credit} credit)")


if __name__ == "__main__":
    run()
