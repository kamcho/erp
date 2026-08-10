"""Seed Grade 8 Tiger students from fee balances sheet (Excel Academy)."""
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
    "MITCHELLE", "LAURA", "SABRINA", "FAITH", "ABIGAEL", "HAJRA", "JOY",
    "TIFFANY", "DIANA", "TASHLEY", "SHIRLEEN", "JEAN", "WARDA", "AGNES",
    "PAMELA", "FAVOUR", "TRACY", "PEACE", "PRECIOUS",
}

# Corrected balances sheet (earlier paste had shifted balances from ~3972).
ROWS = [
    ("2780", "Elizaphan Kiruki", 13800),
    ("2781", "Mitchelle Mumbua", 0),
    ("2783", "Deris Churchil", -1900),
    ("2784", "Laura Wanjiru", 4500),
    ("2810", "Ibrahim Abdiaziz", 93000),
    ("2853", "Sabrina Wangari", 0),
    ("2920", "Faith Achieng", 0),
    ("3081", "Clyde Machayo", 8500),
    ("3101", "Jayden Leshan", -600),
    ("3120", "Sammy Lumire", 4800),
    ("3129", "Galen Wekesa", 10500),
    ("3150", "Abigael Wairimu Ndegwa", 0),
    ("3179", "Andrew Gathimba", 3650),
    ("3215", "Hajra Abdiaziz", 0),
    ("3347", "Joy Lynne Wanjiru Njagi", 0),
    ("3622", "Mohamed Ali Adam", 0),
    ("3648", "Wario Bagajo", 0),
    ("3653", "Kyle Kipkemoi", 0),
    ("3736", "Arthur Mwangi", 0),
    ("3775", "Nahashon Njeru Muriuki", 25000),
    ("3804", "Princehal Dermot", 0),
    ("3830", "Ted Mainga", 4500),
    ("3844", "Bruce Ng'ang'a", 0),
    ("3856", "Tiffany Waithera Matimu", 2500),
    ("3875", "Diana Chepkorir Rop", 2000),
    ("3897", "Tashley Roel", 10600),
    ("3945", "Leeam Njuguna", 5500),
    ("3972", "Shirleen Nyambura Gitonga", 0),
    ("4001", "Jean Maya Wanjiku", -4800),
    ("4011", "Azriel Amisi", 9700),
    ("4034", "Warda Wanjiru", 10500),
    ("4039", "Melchizedek Muli", 0),
    ("4040", "Agnes Mumbe", 0),
    ("4047", "Abdul Bari Mohammed", 0),
    ("4048", "Pamela Akinyi", 28000),
    ("4055", "Teddy Sam Kiunjuri", 6000),
    ("4070", "Favour Naomi Wanjiru", 9600),
    ("4084", "Tracy Majoho", 0),
    ("4104", "Dylan Avi Davies", 0),
    ("4135", "Peace Wangui Mbatia", 0),
    ("4157", "Precious Ozil Kikenda", -500),
    ("4180", "Peter Mwangi Ndungu", 0),
    ("4247", "Faith Abelah Maumba", 0),
    ("4251", "Brighton Gachau", 15200),
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
    if not school or not grade:
        raise SystemExit("Excel Academy / Grade 8 not found")

    klass, _ = Class.objects.get_or_create(
        school=school,
        grade=grade,
        name="Tiger",
    )

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
    from django.db.models import Sum
    total_arrears = StudentProfile.objects.filter(class_id=klass, fee_balance__gt=0).aggregate(s=Sum("fee_balance"))["s"] or 0
    print(f"\nDone. Created {created_n}, updated {updated_n}.")
    print(f"Grade 8 Tiger total: {total} ({owing} owing, {credit} credit, arrears KES {total_arrears})")


if __name__ == "__main__":
    run()
