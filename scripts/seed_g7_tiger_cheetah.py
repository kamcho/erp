"""Seed Grade 7 Tiger (more) + Grade 7 Cheetah."""
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
    "NAVEEN", "JULIA", "ESTHER", "OPRAH", "AISHA", "HELLEN", "BUSHRA", "BLESSING",
    "CYNTHIA", "LARISSA", "MARLIYA", "JOY",
    "JULIE", "MELISSA", "VIVIAN", "JADE", "ANGEL", "ELIZABETH", "ELSA", "ALYSER",
}

BATCHES = [
    (
        "Tiger",
        [
            ("3644", "NAVEEN ESTHER MAIGA", 17000),
            ("3711", "BENNY WANJOHI", 108200),
            ("3714", "SUHEIB MOHAMED", 0),
            ("3730", "STEVE KIMANI", 0),
            ("3731", "JULIA WANGARE MWENJERI", 0),
            ("3794", "PAUL MICKEY WACHIRA", 4800),
            ("3811", "DYLAN LEE KAMAU", 0),
            ("3817", "ZAKARIA BISHAR HUSSEIN", 0),
            ("3889", "ESTHER NJERI MURURI", 10000),
            ("3934", "OPRAH TATIANA", 0),
            ("4026", "ARSENE ASEGA ODERA", 0),
            ("4045", "ABDI KHALIQ ABDI", 14500),
            ("4073", "AISHA ISMAIL", 0),
            ("4120", "HELLEN WANJIRA MWANGI", -24500),
            ("4151", "BUSHRA SHABAN", 0),
            ("4168", "IBRAHIM MUKALA", 9300),
            ("4177", "BLESSING NYAMBURA WARIGI", 0),
            ("4188", "VICTOR MOSE NYABUTO", 0),
            ("4189", "CYNTHIA NJERI MAINA", 0),
            ("4198", "RANDY PHILIP KAMAU", 0),
            ("4209", "LARISSA WANJALA", 0),
            ("4214", "MARLIYA HASSAN", 9600),
            ("4215", "FELIX OMONDI", -5500),
            ("4223", "SIVV IRUNGU KAIRU", 6500),
            ("4243", "JOY NJERI KARANJA", 0),
            ("4248", "JAMES NJENGA NGACHA", -18500),
            ("4262", "MUMIN MANSOOR", 0),
        ],
    ),
    (
        "Cheetah",
        [
            ("3294", "JULIE WAIRIMU", 0),
            ("3303", "OLIVER OOKO", 28900),
            ("3330", "MELISSA GATHIGIA KIMANI", 0),
            ("3343", "GIFT MAINA SIMON", 5900),
            ("3352", "JAMAL KROP", 5400),
            ("3393", "MUAYID HASHI", 6300),
            ("3428", "VIVIAN WAIRIMU", 1000),
            ("3429", "JADE TARAJI", 14500),
            ("3561", "IMMANUEL AIDEN OCHIENG", 0),
            ("3719", "ELDAD JUMA HERNANDEZ", 2400),
            ("3720", "HASTINGS MUNENE", 0),
            ("3957", "TREVOR MUNENE", 0),
            ("4159", "ANGEL MUGURE JOSEPH", 0),
            ("4210", "ELIZABETH KASIVA", 4000),
            ("4216", "ELSA WANJIKU MUCHIRI", 0),
            ("4224", "ALYSER NJERI MBURU", -5500),
            ("4226", "FRANK MUNGAI", 0),
            ("4227", "DENZEL WAKARIA", 0),
            ("4230", "ARNOLD STEVEN", -29500),
        ],
    ),
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


def upsert(school, klass, adm, name, bal):
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
            date_of_birth=DOB,
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
    grade = Grade.objects.filter(name="Grade 7").first()
    if not school or not grade:
        raise SystemExit("Excel Academy / Grade 7 not found")

    created_n = updated_n = 0
    with transaction.atomic():
        for stream, rows in BATCHES:
            klass = Class.objects.filter(school=school, grade=grade, name=stream).first()
            if not klass:
                raise SystemExit(f"Missing Grade 7 / {stream}")
            print(f"\nGrade 7 {stream} (id={klass.id})")
            for adm, name, bal in rows:
                created, student, profile = upsert(school, klass, adm, name, bal)
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
