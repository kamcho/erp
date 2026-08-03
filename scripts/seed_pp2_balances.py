"""Seed PP2 students from fee balances sheet."""
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
    "WAIRIMU", "PATRICIA", "SHANTEL", "JOAN", "THALIA", "BRIDGETTE", "ARRIANA",
    "GIANNA", "ESTHER", "KYLIE", "KELLEN", "MARGARETJOYCE",
}

ROWS = [
    ("3816", "MYLES JUNIOR", 0),
    ("3822", "ISRAEL MANUEL RONALD", 14800),
    ("3834", "WAIRIMU MUTHONI NDIRITU", 0),
    ("3841", "TREVOR KIMANI MWAURA", 0),
    ("3845", "PATRICIA WANJA MAINA", 0),
    ("3849", "BRAYLON NGUMBAU MULI", 0),
    ("3859", "ELLY KINYUA GITHINJI", 0),
    ("3863", "SHAMMAH KIBET KIPKURUI", 0),
    ("3864", "SHANTEL WANGUI WESONGA", 0),
    ("3867", "EARLCADE ELIAN", 0),
    ("3888", "FRANK MUHIA NJOROGE", -500),
    ("3890", "SAMUEL DAVID ASAKA", 0),
    ("3895", "DAVION NICK SAFARI", 0),
    ("3898", "JOAN ALLIEGOLD WANJIKU", 0),
    ("3901", "DAMIAN CALLISTUS ODHIAMB", 0),
    ("3907", "ETHAN MUTAI", 0),
    ("3914", "THALIA GESARE", 14100),
    ("3916", "NILLAN NJUE MWAURA", 32600),
    ("3920", "BRIDGETTE WANJIRU MUKARI", 6700),
    ("3924", "ARRIANA NEMPIRIS", 0),
    ("3925", "GIANNA WACU", 0),
    ("3931", "ESTHER MUTHONI MBUTHIA", 3300),
    ("3940", "KYLIE JAN JUMA", 0),
    ("3941", "HENSLEY KEHLAN NJERI", 1600),
    ("3944", "MICAH KIPKEMOI WANGUI", 7500),
    ("3954", "JIAN KAGIRI GIATOTO", 2650),
    ("3966", "KELLEN DUA ALELO", 0),
    ("3967", "MARGARETJOYCE WANJIKU", 7900),
    ("3970", "GIANNA CHEPCHIRCHIR AGATI", 0),
    ("3993", "NILLAN KINGORI", -700),
]

DOB = date(2020, 6, 1)
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
    grade = Grade.objects.filter(name="PP2").first()
    klass = Class.objects.filter(school=school, grade=grade, name="PP2").first()
    if not school or not klass:
        raise SystemExit("Excel Academy / PP2 class not found")

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
    print(f"PP2 total: {total} ({owing} owing, {credit} credit)")


if __name__ == "__main__":
    run()
