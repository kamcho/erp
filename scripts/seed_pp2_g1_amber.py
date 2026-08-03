"""Seed PP2 continuation + Grade 1 Amber from fee balances sheet."""
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
    "CHLOE", "EMERALD", "ARIEL", "FAITH", "ANGEL",
    "ALICIA", "NEILLAH", "CHARLOTTENYAMBURA", "ETANA", "MARY", "TASMIN",
    "ILHAN", "BLESSING", "GRACE", "AYAN", "LISA", "VANCY", "ORYAN",
}

BATCHES = [
    (
        "PP2",
        "PP2",
        date(2020, 6, 1),
        [
            ("4004", "DAVID MANNA NDERITU", 0),
            ("4032", "CHLOE CHELANGAT", 0),
            ("4037", "JIAN LEVIS KINYUA", 0),
            ("4090", "NATHAN KAMAU", 0),
            ("4105", "SAMMY ELVIS", 12850),
            ("4111", "EMERALD ZAWADI", 4400),
            ("4149", "ARIEL MAGGIE ODUOR", 0),
            ("4162", "ETHAN KAMAU MAINA", 4400),
            ("4181", "FAITH WANGUI CHEGE", 0),
            ("4213", "ANGEL LESHA KABAI", 6500),
        ],
    ),
    (
        "Grade 1",
        "Amber",
        date(2019, 6, 1),
        [
            ("3692", "ALICIA JARENGA NGOTHO", 0),
            ("3698", "ANWYLL BRAISE", 0),
            ("3702", "NEILLAH WANJIRA", 10000),
            ("3706", "ISRAEL MATHEWS MUIGAI", 5000),
            ("3715", "KAYLAN MARLIN", -200),
            ("3717", "CHARLOTTENYAMBURA", 2000),
            ("3722", "DAVID LEWIN AGOLA", 50),
            ("3723", "ETANA AMALI MAINA", 0),
            ("3724", "KAYDEN AMOS OMORIA", 0),
            ("3725", "JAYDEN MOSES OMORIA", 0),
            ("3726", "DALTON PRINCE", 0),
            ("3735", "SAMMY NGIGI MWANGI", 0),
            ("3740", "YAHYA ABDIAZIZ", 50700),
            ("3752", "SULEIMAN RASHID KADIWA", 400),
            ("3772", "MARY MIDINA BAGAJO", 0),
            ("3773", "FRANCIS NJOGU GATHI", 0),
            ("3781", "TASMIN MOHAMMED", 0),
            ("3790", "EZRA KIPROP", 0),
            ("3813", "RYAN NGURE MUGO", 0),
            ("3832", "TREVOR MACHARIA KIGUMI", 0),
            ("3835", "ILHAN HUSSEIN DUBA", 5700),
            ("3947", "BLESSING JASMINE", -700),
            ("3959", "ELIAS CHEGE MIRUGI", 0),
            ("3960", "ERIC JADEN OMONDI", 0),
            ("4021", "LEVI GATHUNGU GITHINJI", 0),
            ("4041", "LIAM MUTUA", 700),
            ("4059", "GRACE KASERA", 0),
            ("4076", "AYAN WANJIKU NGARI", 5400),
            ("4089", "KYLE KAMAU", -100),
            ("4092", "AADIL TARUJIA", 4800),
            ("4108", "IVAN JUMA", -1000),
            ("4118", "LEWIN NGUU GACHUHI", 0),
            ("4172", "LISA JANE CLARKE", 0),
            ("4192", "VANCY NJAMBI", 0),
            ("4195", "ORYAN NJERI MUNGAI", 1900),
            ("4207", "ALI BISHAR HUSSEIN", 16500),
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
