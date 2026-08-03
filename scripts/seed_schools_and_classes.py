"""
Seed/cleanup schools, grades, and class streams.

Class naming rules:
- Play Group / PP1 / PP2: stream name = grade level (e.g. "PP1", not "Indigo")
- Grade 1–6: Amber, Indigo
- Grade 7–9: Cheetah, Tiger

Only Excel Academy is kept; other schools are removed.
Students are reassigned class-by-class to the matching Academy stream.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Excel.settings")

import django

django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

from core.models import School, Grade, Class, StudentProfile

KEEP_SCHOOL = "Excel Academy"
GRADE_NAMES = [
    "Play Group", "PP1", "PP2",
    "Grade 1", "Grade 2", "Grade 3",
    "Grade 4", "Grade 5", "Grade 6",
    "Grade 7", "Grade 8", "Grade 9",
]
PRE_PRIMARY = {"Play Group", "PP1", "PP2"}


def streams_for_grade(grade_name: str) -> list[str]:
    if grade_name in PRE_PRIMARY:
        return [grade_name]

    if grade_name.startswith("Grade"):
        try:
            num = int(grade_name.split()[-1])
        except (ValueError, IndexError):
            return ["Amber", "Indigo"]
        if 1 <= num <= 6:
            return ["Amber", "Indigo"]
        if 7 <= num <= 9:
            return ["Cheetah", "Tiger"]

    return ["Amber", "Indigo"]


def ensure_academy() -> School:
    school, created = School.objects.get_or_create(
        name=KEEP_SCHOOL,
        defaults={
            "address": "Nairobi, Kenya",
            "phone": "0700000000",
            "email": "excelacademy@excelschools.com",
        },
    )
    print(f"{'Created' if created else 'Found'} school: {school.name}")
    return school


def ensure_grades() -> list[Grade]:
    grades = []
    for g_name in GRADE_NAMES:
        grade, created = Grade.objects.get_or_create(name=g_name)
        print(f"{'Created' if created else 'Found'} grade: {grade.name}")
        grades.append(grade)
    return grades


def expected_stream_name(grade: Grade, current_name: str) -> str:
    if grade.name in PRE_PRIMARY:
        return grade.name
    return current_name


def canonicalize_pre_primary_streams(school: School, grade: Grade) -> Class:
    """Ensure one class named after the grade; merge any Indigo/legacy streams into it."""
    target_name = grade.name
    target = Class.objects.filter(school=school, grade=grade, name=target_name).first()
    legacy_qs = Class.objects.filter(school=school, grade=grade).exclude(name=target_name)

    if not target and legacy_qs.exists():
        target = legacy_qs.order_by("id").first()
        old = target.name
        target.name = target_name
        target.save(update_fields=["name"])
        print(f"Renamed: {school.name} / {grade.name} {old!r} -> {target_name!r}")
        legacy_qs = Class.objects.filter(school=school, grade=grade).exclude(pk=target.pk)

    if not target:
        target = Class.objects.create(school=school, grade=grade, name=target_name)
        print(f"Created class: {school.name} / {grade.name} / {target_name}")
        return target

    for legacy in list(legacy_qs):
        moved = StudentProfile.objects.filter(class_id=legacy).update(class_id=target)
        if moved:
            print(
                f"Moved {moved} student(s) from "
                f"{school.name}/{grade.name}/{legacy.name} -> {target_name}"
            )
        print(f"Deleted duplicate stream: {school.name} / {grade.name} / {legacy.name}")
        legacy.delete()

    return target


def ensure_academy_classes(academy: School, grades: list[Grade]) -> int:
    created_count = 0
    for grade in grades:
        if grade.name in PRE_PRIMARY:
            canonicalize_pre_primary_streams(academy, grade)
            continue

        for stream in streams_for_grade(grade.name):
            _, created = Class.objects.get_or_create(
                school=academy,
                grade=grade,
                name=stream,
            )
            if created:
                created_count += 1
                print(f"Created class: {academy.name} / {grade.name} / {stream}")
    return created_count


def find_academy_class(academy: School, source: Class) -> Class | None:
    wanted = expected_stream_name(source.grade, source.name)
    match = Class.objects.filter(
        school=academy, grade=source.grade, name=wanted
    ).first()
    if match:
        return match
    return Class.objects.filter(school=academy, grade=source.grade).order_by("id").first()


def delete_other_schools(academy: School) -> int:
    others = list(School.objects.exclude(pk=academy.pk))
    deleted = 0
    User = get_user_model()

    for school in others:
        print(f"\nRemoving school: {school.name}")

        # Move students class-by-class (never filter by school alone while looping classes)
        for klass in list(Class.objects.filter(school=school).select_related("grade")):
            target = find_academy_class(academy, klass)
            class_profiles = StudentProfile.objects.filter(class_id=klass)
            count = class_profiles.count()
            if count:
                if target:
                    class_profiles.update(school=academy, class_id=target)
                    print(
                        f"  Reassigned {count} student(s): "
                        f"{school.name}/{klass.grade.name}/{klass.name} "
                        f"-> {academy.name}/{target.grade.name}/{target.name}"
                    )
                else:
                    class_profiles.update(school=academy, class_id=None)
                    print(
                        f"  Reassigned {count} student(s): "
                        f"{school.name}/{klass.grade.name}/{klass.name} "
                        f"-> {academy.name} (no matching class)"
                    )

        # Profiles still pointing at this school (no class / already moved class)
        leftover = StudentProfile.objects.filter(school=school)
        leftover_count = leftover.count()
        if leftover_count:
            leftover.update(school=academy)
            print(f"  Updated school on {leftover_count} leftover profile(s)")

        moved_users = User.objects.filter(school=school).update(school=academy)
        if moved_users:
            print(f"  Reassigned {moved_users} user(s) to {academy.name}")

        school_name = school.name
        # Cascades classes and school-scoped config after students/users are moved
        school.delete()
        deleted += 1
        print(f"Deleted school: {school_name}")

    return deleted


def run():
    with transaction.atomic():
        academy = ensure_academy()
        grades = ensure_grades()
        created_count = ensure_academy_classes(academy, grades)
        deleted_schools = delete_other_schools(academy)

        # Final pass on remaining schools (Academy only)
        for grade_name in PRE_PRIMARY:
            grade = Grade.objects.filter(name=grade_name).first()
            if grade:
                canonicalize_pre_primary_streams(academy, grade)

    total = Class.objects.filter(school=academy).count()
    print(
        f"\nDone. Academy classes created this run: {created_count}. "
        f"Schools deleted: {deleted_schools}. "
        f"Total Academy classes: {total}."
    )
    print("Remaining schools:", list(School.objects.values_list("name", flat=True)))
    print("Pre-primary streams:")
    for c in Class.objects.filter(
        grade__name__in=PRE_PRIMARY
    ).select_related("school", "grade").order_by("grade__name", "name"):
        print(f"  {c.school.name} / {c.grade.name} / {c.name}")


if __name__ == "__main__":
    run()
