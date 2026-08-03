"""
Seed schools, grades, and class streams.

Class naming rules:
- Play Group / PP1 / PP2: class name = grade level (e.g. "PP1")
- Grade 1–6: Amber, Indigo
- Grade 7–9: Cheetah, Tiger
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Excel.settings")

import django

django.setup()

from core.models import School, Grade, Class

SCHOOLS = ["Excel Academy", "Excel Grassland", "Excel Greenland"]

GRADE_NAMES = [
    "Play Group", "PP1", "PP2",
    "Grade 1", "Grade 2", "Grade 3",
    "Grade 4", "Grade 5", "Grade 6",
    "Grade 7", "Grade 8", "Grade 9",
]

PRE_PRIMARY = {"Play Group", "PP1", "PP2"}


def streams_for_grade(grade_name: str) -> list[str]:
    if grade_name in PRE_PRIMARY:
        # Class name is the grade level itself
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


def run():
    schools = []
    for name in SCHOOLS:
        school, created = School.objects.get_or_create(
            name=name,
            defaults={
                "address": "Nairobi, Kenya",
                "phone": "0700000000",
                "email": f"{name.lower().replace(' ', '')}@excelschools.com",
            },
        )
        print(f"{'Created' if created else 'Found'} school: {school.name}")
        schools.append(school)

    grades = []
    for g_name in GRADE_NAMES:
        grade, created = Grade.objects.get_or_create(name=g_name)
        print(f"{'Created' if created else 'Found'} grade: {grade.name}")
        grades.append(grade)

    created_count = 0
    renamed_count = 0

    for school in schools:
        for grade in grades:
            for stream in streams_for_grade(grade.name):
                # For pre-primary, rename legacy "Indigo" stream to the grade name
                if grade.name in PRE_PRIMARY:
                    legacy = Class.objects.filter(
                        school=school, grade=grade, name="Indigo"
                    ).first()
                    if legacy and legacy.name != stream:
                        legacy.name = stream
                        legacy.save(update_fields=["name"])
                        renamed_count += 1
                        print(f"Renamed: {school.name} / {grade.name} Indigo -> {stream}")

                klass, created = Class.objects.get_or_create(
                    school=school,
                    grade=grade,
                    name=stream,
                )
                if created:
                    created_count += 1
                    print(f"Created class: {school.name} / {grade.name} / {stream}")

    total = Class.objects.filter(school__in=schools).count()
    print(
        f"\nDone. Created {created_count} classes, renamed {renamed_count}. "
        f"Total classes across schools: {total}"
    )


if __name__ == "__main__":
    run()
