"""Seed G3 Amber more, G3 Indigo, G4 Amber start. '-' = 0."""
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
    "SARAH", "LIZZETTE", "JOY", "LESLIE", "MARYANNE",
    "DESTINY", "ABIGAEL", "SUSAN", "LEILAH", "HYME", "ARIANNAH", "ZAIDA",
    "PRINCESS", "ANNABELLE", "MERCY", "BRIELLA", "IMMACULATE", "CHARLENE", "AYNI",
    "THANDI", "MILLAN",
}

BATCHES = [
    (
        "Grade 3",
        "Amber",
        date(2017, 6, 1),
        [
            ("3935", "SARAH MIRA BINSARI", 700),
            ("4022", "DANIEL KAGOMBE GITHINJI", 0),
            ("4080", "HESLY MBURU NJENGA", 800),
            ("4081", "LIZZETTE MAKENA", 0),
            ("4116", "JOY WANJIKU WAIGURU", -200),
            ("4126", "MOHAMMED JIBRIL", 0),
            ("4146", "LESLIE MAIGA", 0),
            ("4179", "JAYDEN MUIGAI", -300),
            ("4204", "ZAKARIYA OSMAN BASHIR", 0),
            ("4258", "MARYANNE MELSON", 7000),
        ],
    ),
    (
        "Grade 3",
        "Indigo",
        date(2017, 6, 1),
        [
            ("3854", "DESTINY HOPE HADASAH", 100),
            ("3860", "ABIGAEL WANJIKU GITHINJI", 0),
            ("3865", "ELLISON MUHORA NEDGWA", 0),
            ("3868", "SUSAN NGENDO", 0),
            ("3874", "LEILAH ALISON AKIDA", 0),
            ("3881", "JOY TIFFANY WAMBUI", 0),
            ("3887", "HYME WANGU SAITOTI", 0),
            ("3891", "ETHAN MAINA MWANGI", 0),
            ("3900", "ARIANNAH CHEBET", 0),
            ("3903", "JAYSON MILES", 700),
            ("3908", "ZAIDA MOHAMED ABDI", 0),
            ("3928", "CORNELIUS MATHENGE", 200),
            ("3938", "ETHAN MUNDIA MUCHINA", 0),
            ("3946", "PRINCESS LINA KARJUKI", 3100),
            ("3989", "ANNABELLE WAMBUI", -750),
            ("4008", "JOY WANJIRU MACHARIA", 0),
            ("4029", "BRYCE WALTER OGAMBA", 1800),
            ("4049", "MERCY MUKAMBURI", 17200),
            ("4087", "LEMUEL KAMAU", 0),
            ("4098", "RYAN MUGO WAGEMA", 7100),
            ("4123", "ISAAC MUTHUI NJAGI", 0),
            ("4141", "BRIELLA CHEPCHUMBA", 0),
            ("4145", "JAMIEL RICKY", -6600),
            ("4150", "IMMACULATE ASHLEY", 0),
            ("4165", "JOY WAMBUI MAINA", 0),
            ("4174", "CHARLENE WANGU KINYUA", 0),
            ("4232", "RAYYAN AYUB", 45300),
            ("4256", "AYNI MUHAMMUD", 20100),
        ],
    ),
    (
        "Grade 4",
        "Amber",
        date(2016, 6, 1),
        [
            ("3275", "THANDI NJAI SOITA", 0),
            ("3283", "ABIGAEL MKANGOMBE WARA", -700),
            ("3290", "ISAKO BAGAJO", 0),
            ("3293", "LEON MAINA MUTHUTHIRI", 0),
            ("3302", "MILLAN KABUTU", 3900),
            ("3308", "JAYSON GATUA", 0),
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
