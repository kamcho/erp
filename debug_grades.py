
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Excel.settings')
django.setup()

from core.models import Grade, StudentProfile

print("GRADES:")
for g in Grade.objects.all():
    count = StudentProfile.objects.filter(class_id__grade=g).count()
    print(f"ID: {g.id}, Name: {g.name}, Student Count: {count}")

print("\nSTUDENT EA-0013:")
s = StudentProfile.objects.filter(student__adm_no='EA-0013').first()
if s:
    print(f"Name: {s.student.get_full_name()}")
    print(f"Grade: {s.class_id.grade.name if s.class_id else 'None'}")
    print(f"Grade ID: {s.class_id.grade.id if s.class_id else 'None'}")
    print(f"School: {s.school.name if s.school else 'None'}")
    print(f"Status: {s.status}")
else:
    print("EA-0013 not found in profiles.")

print("\nSTUDENT EA-0014:")
s = StudentProfile.objects.filter(student__adm_no='EA-0014').first()
if s:
    print(f"Name: {s.student.get_full_name()}")
    print(f"Grade: {s.class_id.grade.name if s.class_id else 'None'}")
    print(f"Grade ID: {s.class_id.grade.id if s.class_id else 'None'}")
    print(f"Status: {s.status}")
