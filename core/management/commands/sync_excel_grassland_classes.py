"""
Create/sync Excel Grassland school and class streams.

Stream naming:
- Play Group / PP1 / PP2: class name matches grade level
- Grade 1 & 3: East / West
- Grade 2, 4, 5, 6, 8: single class per grade (class name = grade name)
- Grade 7 & 9: Everest (E) / Amazon (A)
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Class, Grade, School

SCHOOL_NAME = "Excel Grassland"

# (grade_name, class_stream_name)
GRASSLAND_CLASSES = [
    ("Play Group", "Play Group"),
    ("PP1", "PP1"),
    ("PP2", "PP2"),
    ("Grade 1", "East"),
    ("Grade 1", "West"),
    ("Grade 2", "Grade 2"),
    ("Grade 3", "East"),
    ("Grade 3", "West"),
    ("Grade 4", "Grade 4"),
    ("Grade 5", "Grade 5"),
    ("Grade 6", "Grade 6"),
    ("Grade 7", "Everest"),
    ("Grade 7", "Amazon"),
    ("Grade 8", "Grade 8"),
    ("Grade 9", "Everest"),
    ("Grade 9", "Amazon"),
]


class Command(BaseCommand):
    help = "Create Excel Grassland (if missing) and sync its class streams."

    def handle(self, *args, **options):
        with transaction.atomic():
            school, school_created = School.objects.get_or_create(
                name=SCHOOL_NAME,
                defaults={
                    "address": "Nairobi, Kenya",
                    "phone": "0700000000",
                    "email": "grassland@excelschools.com",
                },
            )
            if school_created:
                self.stdout.write(self.style.SUCCESS(f"Created school: {school.name}"))
            else:
                self.stdout.write(f"Found school: {school.name}")

            created = 0
            existing = 0
            for grade_name, stream_name in GRASSLAND_CLASSES:
                grade, _ = Grade.objects.get_or_create(name=grade_name)
                _, was_created = Class.objects.get_or_create(
                    school=school,
                    grade=grade,
                    name=stream_name,
                )
                if was_created:
                    created += 1
                    self.stdout.write(f"  + {grade_name} / {stream_name}")
                else:
                    existing += 1

            total = Class.objects.filter(school=school).count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Done. Created {created}, already existed {existing}. "
                    f"Total classes at {SCHOOL_NAME}: {total}."
                )
            )
