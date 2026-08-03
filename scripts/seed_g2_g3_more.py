"""Seed G2 Amber more, G2 Indigo, G3 Amber. '-' outstanding = 0."""
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
    "CATE", "BRIANNA", "MELANY", "RENEE", "SANDRA", "AMARA", "TIFFANY", "MARGARET",
    "LYNN", "LYNNE", "PRECIOUS", "ADNA",
    "MYRA", "BIANKA", "SHANTEL", "BRYLE", "ZAWADI", "PATIENCE", "LUCIA", "LEILANI",
    "NATALIA", "MERCY",
}

BATCHES = [
    (
        "Grade 2",
        "Amber",
        date(2018, 6, 1),
        [
            ("4079", "JASPER MUNGAI NJENGA", -4200),
            ("4083", "COLLINS LWAMBI", 0),
            ("4143", "CATE NYAMBURA", 0),
            ("4161", "BRIANNA JERUTO KENYANI", 0),
            ("4185", "MELANY JESIRE", 1850),
        ],
    ),
    (
        "Grade 2",
        "Indigo",
        date(2018, 6, 1),
        [
            ("3973", "RENEE WANJIRU", 0),
            ("3976", "LUCIAN KHALID", 0),
            ("3983", "MYLES BREN WANDERA", 3800),
            ("3996", "SANDRA LEE TABITHA", 200),
            ("3998", "AMARA NYAKOA JOSAM", 0),
            ("4002", "DANNY WILLIAMS", -3500),
            ("4005", "TIFFANY WANJERI", 0),
            ("4006", "MARGARET WANGU NGUGI", 0),
            ("4017", "LYNN JEBET KIPTUM", 3200),
            ("4030", "LEON WAVERU KARIUKI", 9800),
            ("4035", "LYNNE HEAVELY", 5500),
            ("4051", "JAYDEN KABIRU GATURO", 14800),
            ("4119", "TRAVIS IMANI KIPROP", 0),
            ("4164", "ADRIAN KIMUTAI NGENO", 0),
            ("4208", "ADNA BISHAR", 0),
            ("4219", "RYAN MUTUA MUKUI", 0),
            ("4221", "PRECIOUS JEMUTAI RUTTO", 0),
            ("4263", "TREVOR THUO", 0),
        ],
    ),
    (
        "Grade 3",
        "Amber",
        date(2017, 6, 1),
        [
            ("3469", "EPHRAIM AMANI", 0),
            ("3472", "MYRA WANJIKU", 0),
            ("3476", "BIANKA WANGARI NDUNGU", 0),
            ("3482", "COLLINS AGWATA", 0),
            ("3483", "SHANTEL BWARI", 0),
            ("3492", "BRYLE MUKAMI", 0),
            ("3511", "DOUGLAS GITHINJI", 0),
            ("3512", "TROY WILLIAMS MIYOGO", 0),
            ("3518", "ELVIS LEVI NDUNGU", 0),
            ("3530", "ZAWADI WANJIRU", 15200),
            ("3534", "DYLAN NDERITU KONDIAN", 0),
            ("3536", "PATIENCE MUTHONI NG'ANG'A", 0),
            ("3547", "LUCIA LEONE AGOLA", 12650),
            ("3647", "LEILANI CHELANGAT", 0),
            ("3699", "RYAN MESO", 0),
            ("3751", "SHAWN NICHOLAS AGESA", 0),
            ("3789", "NATALIA NYAMBONYI NYAMA", 0),
            ("3831", "TIM MAINGA", 0),
            ("3833", "LIAM MWANGI KIGUMI", 0),
            ("3837", "MERCY WANJIRU KARIUKI", 700),
            ("3917", "JAYDEN JUNIOR NYONGESA", 100),
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
