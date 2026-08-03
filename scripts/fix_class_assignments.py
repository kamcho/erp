"""
Fix class assignments from clarified page map:
- img13: 9 Cheetah + 8 Cheetah  (former STD 9B -> G8 Cheetah; 9I stays G9 Cheetah)
- img14: 9 Cheetah total + 9 Tiger students (former PC -> G9 Tiger)
- img10: 6A + 6I + 7 Tiger (G6I 'additional' block -> G7 Tiger)
- 9C = Cheetah (not a PC stream)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Excel.settings")

import django

django.setup()

from django.db import transaction
from core.models import School, Grade, Class, StudentProfile

# Former STD 9B (img13) — should be Grade 8 Cheetah
G8_CHEETAH_ADMS = [
    "2777", "2804", "2861", "3000", "3093", "3105", "3128", "3142", "3147", "3157",
    "3188", "3170", "3204", "3315", "3402", "3424", "3509", "3529", "3668", "3689",
    "3710", "3718", "4027", "4042", "4062", "4100", "4113", "4170", "4193", "4201",
    "4228", "4260",
]

# Former STD PC (img14) — should be Grade 9 Tiger
G9_TIGER_ADMS = [
    "2746", "2765", "2893", "2895", "2953", "2958", "2962", "2963", "2971", "2990",
    "3251", "3442", "3508", "3605", "3645", "3650", "3686", "3788", "3826", "3828",
    "3842", "3857", "3861", "3896", "3902", "3909", "4031", "4137", "4175",
]

# G6 Indigo "additional" block from img10 — should be Grade 7 Tiger
G7_TIGER_FROM_IMG10 = [
    "008", "026", "029", "038", "052",
    "2842", "2867", "2883", "2946", "2984", "3052", "3214", "3256", "3258",
    "3271", "3272", "3273", "3305", "3447", "3623",
]


def get_class(school, grade_name, stream):
    grade = Grade.objects.get(name=grade_name)
    klass, created = Class.objects.get_or_create(
        school=school, grade=grade, name=stream
    )
    if created:
        print(f"Created class {grade_name} / {stream} id={klass.id}")
    return klass


def move_adms(school, adms, grade_name, stream):
    klass = get_class(school, grade_name, stream)
    moved = 0
    missing = []
    for adm in adms:
        profile = StudentProfile.objects.filter(
            student__adm_no=str(adm), school=school
        ).select_related("student", "class_id").first()
        if not profile:
            missing.append(adm)
            continue
        old = f"{profile.class_id.grade.name}/{profile.class_id.name}" if profile.class_id else "None"
        profile.class_id = klass
        profile.save(update_fields=["class_id"])
        moved += 1
        print(f"  {adm} {profile.student.get_full_name()}: {old} -> {grade_name}/{stream}")
    if missing:
        print(f"  Missing adm nos: {missing}")
    return moved


def run():
    school = School.objects.filter(name__iexact="Excel Academy").first()
    if not school:
        raise SystemExit("Excel Academy not found")

    with transaction.atomic():
        print("\n1) Former STD 9B -> Grade 8 Cheetah")
        n1 = move_adms(school, G8_CHEETAH_ADMS, "Grade 8", "Cheetah")

        print("\n2) Former STD PC / img14 list -> Grade 9 Tiger")
        n2 = move_adms(school, G9_TIGER_ADMS, "Grade 9", "Tiger")

        print("\n3) img10 G6I additional block -> Grade 7 Tiger")
        n3 = move_adms(school, G7_TIGER_FROM_IMG10, "Grade 7", "Tiger")

        # Remove empty PC class if unused
        pc = Class.objects.filter(school=school, grade__name="Grade 9", name="PC").first()
        if pc:
            left = StudentProfile.objects.filter(class_id=pc).count()
            if left == 0:
                pc.delete()
                print("\nDeleted empty Grade 9 / PC class")
            else:
                print(f"\nGrade 9 / PC still has {left} students — not deleted")

    print("\nFinal counts:")
    for g, n in [
        ("Grade 6", "Amber"),
        ("Grade 6", "Indigo"),
        ("Grade 7", "Tiger"),
        ("Grade 7", "Cheetah"),
        ("Grade 8", "Tiger"),
        ("Grade 8", "Cheetah"),
        ("Grade 9", "Tiger"),
        ("Grade 9", "Cheetah"),
    ]:
        klass = Class.objects.filter(school=school, grade__name=g, name=n).first()
        if klass:
            print(f"  {g} {n}: {StudentProfile.objects.filter(class_id=klass).count()}")

    print(f"\nMoved: {n1} to G8 Cheetah, {n2} to G9 Tiger, {n3} to G7 Tiger")


if __name__ == "__main__":
    run()
