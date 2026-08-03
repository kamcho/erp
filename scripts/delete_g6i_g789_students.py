"""Delete all students in Grade 6 Indigo and all Grade 7/8/9 classes."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Excel.settings")

import django

django.setup()

from django.db import transaction
from core.models import School, Class, Student, StudentProfile

TARGETS = [
    ("Grade 6", "Indigo"),
    ("Grade 7", None),  # all streams
    ("Grade 8", None),
    ("Grade 9", None),
]


def run():
    school = School.objects.filter(name__iexact="Excel Academy").first()
    if not school:
        raise SystemExit("Excel Academy not found")

    classes = []
    for grade_name, stream in TARGETS:
        qs = Class.objects.filter(school=school, grade__name=grade_name)
        if stream:
            qs = qs.filter(name=stream)
        found = list(qs)
        if not found:
            print(f"No classes for {grade_name} / {stream or 'ALL'}")
        for c in found:
            classes.append(c)
            print(f"Target class: {c.grade.name} / {c.name} (id={c.id})")

    profiles = StudentProfile.objects.filter(class_id__in=classes).select_related("student")
    student_ids = list(profiles.values_list("student_id", flat=True))
    print(f"\nProfiles to remove: {profiles.count()}")
    print(f"Students to delete: {len(student_ids)}")

    with transaction.atomic():
        # Delete students (cascades profile and most related rows)
        deleted, details = Student.objects.filter(id__in=student_ids).delete()
        print(f"Deleted objects: {deleted}")
        for model, count in details.items():
            print(f"  {model}: {count}")

    print("\nRemaining in targeted classes:")
    for c in classes:
        left = StudentProfile.objects.filter(class_id=c).count()
        print(f"  {c.grade.name} / {c.name}: {left}")


if __name__ == "__main__":
    run()
