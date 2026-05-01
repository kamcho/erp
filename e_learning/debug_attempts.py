import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Excel.settings')
django.setup()

from e_learning.models import Quiz, QuizAttempt, Assignment, AssignmentAttempt
from Exam.models import Subject

def debug_subject(subject_id):
    subject = Subject.objects.get(pk=subject_id)
    print(f"Subject: {subject.name} (ID: {subject.id})")
    
    quizzes = Quiz.objects.filter(subject=subject)
    print(f"Quizzes found: {quizzes.count()}")
    for q in quizzes:
        qa_count = QuizAttempt.objects.filter(quiz=q).count()
        qa_completed = QuizAttempt.objects.filter(quiz=q).exclude(status='in_progress').count()
        aa_count = AssignmentAttempt.objects.filter(assignment__quiz=q).count()
        aa_completed = AssignmentAttempt.objects.filter(assignment__quiz=q).exclude(status='in_progress').count()
        print(f"  - Quiz: {q.title} (ID: {q.id})")
        print(f"    Direct Attempts: {qa_count} (Completed: {qa_completed})")
        print(f"    Assignment Attempts: {aa_count} (Completed: {aa_completed})")

    assignments = Assignment.objects.filter(subject=subject)
    print(f"Assignments found: {assignments.count()}")
    for a in assignments:
        aa_count = AssignmentAttempt.objects.filter(assignment=a).count()
        aa_completed = AssignmentAttempt.objects.filter(assignment=a).exclude(status='in_progress').count()
        print(f"  - Assignment: {a.title} (ID: {a.id})")
        print(f"    Attempts: {aa_count} (Completed: {aa_completed})")

if __name__ == "__main__":
    print(f"Total QuizAttempts: {QuizAttempt.objects.count()}")
    print(f"  - Completed: {QuizAttempt.objects.exclude(status='in_progress').count()}")
    print(f"Total AssignmentAttempts: {AssignmentAttempt.objects.count()}")
    print(f"  - Completed: {AssignmentAttempt.objects.exclude(status='in_progress').count()}")
    
    # Check most recent attempts
    print("\nRecent 5 QuizAttempts:")
    for qa in QuizAttempt.objects.all().order_by('-id')[:5]:
        print(f"  - ID: {qa.id}, Quiz: {qa.quiz.title}, Student: {qa.student}, Status: {qa.status}")

    print("\nRecent 5 AssignmentAttempts:")
    for aa in AssignmentAttempt.objects.all().order_by('-id')[:5]:
        quiz_title = aa.assignment.quiz.title if aa.assignment.quiz else "N/A"
        print(f"  - ID: {aa.id}, Assignment: {aa.assignment.title}, Quiz: {quiz_title}, Student: {aa.student}, Status: {aa.status}")

