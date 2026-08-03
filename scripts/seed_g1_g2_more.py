"""Seed Grade 1 Amber continuation, Grade 1 Indigo, Grade 2 Amber."""
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
    "GIANNA", "ROSE", "TRISHIA", "DUYA", "KENZIAH", "TIFFANY", "REHEMA", "PATIENCE",
    "JANE", "AMAYA", "JENNY", "JASMINE", "MARY", "ELSIE", "JOYCE", "ABIGAIL",
    "VICTORIA", "SHANI", "PROMISE", "CHARLOTTE", "ANNETTE", "MERCYLINE", "LADINA",
}

BATCHES = [
    (
        "Grade 1",
        "Amber",
        date(2019, 6, 1),
        [
            ("4217", "GIANNA WANJIRU", 0),
            ("4231", "JAYSON OINO NYAMBANE", 4300),
            ("4244", "ROSE VALENTINE", 105450),
        ],
    ),
    (
        "Grade 1",
        "Indigo",
        date(2019, 6, 1),
        [
            ("4121", "TRISHIA MURUGI MWANGI", -15000),
            ("4131", "ALEX MWAURA", 0),
            ("4133", "DUYA CARILLA DESTINY", 0),
            ("4154", "KENZIAH MUHONJA", 0),
            ("4220", "TIFFANY WANJA GATURO", 14800),
            ("4234", "REHEMA RUTH WANJIRU", 0),
            ("4257", "PATIENCE WAMBUI", 500),
        ],
    ),
    (
        "Grade 2",
        "Amber",
        date(2018, 6, 1),
        [
            ("3548", "JANE NJERI KARIRUKI", 0),
            ("3554", "TIFFANY GRACE SEMO", 3600),
            ("3558", "JAYSON NG'ANG'A", 5200),
            ("3564", "AMAYA WAITHERA", 0),
            ("3568", "SMURF HEHO NGANGA", 10000),
            ("3573", "JENNY SHANTEL", 12200),
            ("3581", "JASMINE GATOTO", 5350),
            ("3590", "RYAN NYABIKA OBWAYA", 3600),
            ("3597", "MARY WAIRIMU NJERI", 0),
            ("3602", "ELSIE NJERI NDIINI", 0),
            ("3607", "KING BRIGHT WAINAINA", 25400),
            ("3612", "SHEM DULLU BISSANI", 0),
            ("3614", "AUSTIN MUTWIRI GITONGA", 0),
            ("3630", "NICKLAUS MUIGAI", 5700),
            ("3649", "JOYCE WANGU KUNGU", 0),
            ("3665", "MARY HERONE", 0),
            ("3721", "ABIGAIL GLORIA", 0),
            ("3764", "MOEN MWANGI MWAURA", 52600),
            ("3778", "JAMIE KIPLANGAT SOITA", 0),
            ("3806", "STEVEN KAMUTHU", 0),
            ("3829", "KYLE JAY JUMA", 7700),
            ("3858", "JEROBOAM MASESE MOGANE", 3300),
            ("3884", "VICTORIA NOAISHI KOSEN", 0),
            ("3911", "SETH IMANI", 0),
            ("3913", "SHANI WAMBUI", 0),
            ("3919", "ISMAIL ABDI", 5000),
            ("3971", "PROMISE MUIGAI", 3800),
            ("3981", "CHARLOTTE AMOR", -4600),
            ("3987", "JACEALLAN MBURU", 5500),
            ("3990", "ANNETTE MUMBI", -750),
            ("4019", "MERCYLINE WANJIKU", 0),
            ("4023", "MICHAEL KYLE MWANGI", 0),
            ("4053", "LADINA WAFASHU SIMON", 0),
            ("4068", "ZAKARY MUKALA", 0),
        ],
    ),
]

JOINED = date(2026, 1, 5)


def split_name(full: str):
    parts = [p for p in full.strip().split() if p]
    if len(parts) == 1:
        return parts[0].title(), "", parts[0].title()
    if len(parts) == 2:
        return parts[0].title(), "", parts[1].title()
    return parts[0].title(), " ".join(parts[1:-1]).title(), parts[-1].title()


def upsert(school, klass, adm, name, bal, dob):
    first, middle, last = split_name(name)
    gender = "female" if first.upper() in FEMALE_FIRST else "male"
    student = Student.objects.filter(adm_no=str(adm)).first()
    created = False
    if not student:
        student = Student(
            adm_no=str(adm),
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
    return created, student, profile


def run():
    school = School.objects.filter(name__iexact="Excel Academy").first()
    if not school:
        raise SystemExit("Excel Academy not found")

    created_n = updated_n = 0
    with transaction.atomic():
        for grade_name, stream, dob, rows in BATCHES:
            grade = Grade.objects.filter(name=grade_name).first()
            klass = Class.objects.filter(school=school, grade=grade, name=stream).first()
            if not klass:
                raise SystemExit(f"Missing class: {grade_name} / {stream}")
            print(f"\n{grade_name} {stream} (id={klass.id})")
            for adm, name, bal in rows:
                created, student, profile = upsert(school, klass, adm, name, bal, dob)
                if created:
                    created_n += 1
                    tag = "Created"
                else:
                    updated_n += 1
                    tag = "Updated"
                print(f"  {tag}: {adm} {student.get_full_name()} balance={profile.fee_balance}")

            total = StudentProfile.objects.filter(class_id=klass).count()
            owing = StudentProfile.objects.filter(class_id=klass, fee_balance__gt=0).count()
            credit = StudentProfile.objects.filter(class_id=klass, fee_balance__lt=0).count()
            print(f"  -> class total: {total} ({owing} owing, {credit} credit)")

    print(f"\nDone. Created {created_n}, updated {updated_n}.")


if __name__ == "__main__":
    run()
