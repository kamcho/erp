
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Excel.settings')
django.setup()

from accounts.models import FeeStructure
from core.models import Term, Grade

active_term = Term.objects.filter(is_active=True).first()

print("\nEXISTING FEE STRUCTURES FOR ACTIVE TERM:")
fs_list = FeeStructure.objects.filter(term=active_term)
for fs in fs_list:
    grades = ", ".join([g.name for g in fs.grade.all()])
    print(f"ID: {fs.id}, Name: {fs.name}, School: {fs.school.name if fs.school else 'All'}, Type: {fs.student_type}, Amount: {fs.amount}, Grades: [{grades}]")
