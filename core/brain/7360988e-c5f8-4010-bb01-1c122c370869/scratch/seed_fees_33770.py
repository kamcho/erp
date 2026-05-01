import os
import sys
import django

# Add project root to path
sys.path.append(r'c:\Users\USER\Downloads\ERP\SMS-main')
from datetime import date, timedelta
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Excel.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from core.models import Student, StudentProfile, AcademicYear, Term, School
from accounts.models import (
    Invoice, Payment,
    AuxiliaryServiceType, AuxiliaryCharge, AuxiliaryPayment
)

def seed_financials():
    try:
        student = Student.objects.get(pk=33770)
        print(f"Found student: {student.get_full_name()}")
    except Student.DoesNotExist:
        print("Student with ID 33770 not found.")
        return

    profile = student.studentprofile
    school = profile.school

    # Get a user to record payments
    recorder = User.objects.filter(is_superuser=True).first()
    if not recorder:
        recorder = User.objects.first()

    # Academic Year
    year_2026 = AcademicYear.objects.filter(is_active=True).first()
    if not year_2026:
        year_2026, _ = AcademicYear.objects.get_or_create(
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            defaults={'is_active': True}
        )

    # Terms
    term1 = Term.objects.filter(name__icontains='Term 1').first()
    term2 = Term.objects.filter(name__icontains='Term 2').first()
    
    if not term1:
        term1, _ = Term.objects.get_or_create(name="Term 1", defaults={'is_active': False})
    if not term2:
        term2, _ = Term.objects.get_or_create(name="Term 2", defaults={'is_active': True})
    
    print(f"Using Term 1: {term1} (id={term1.id})")
    print(f"Using Term 2: {term2} (id={term2.id})")
    print(f"Using Academic Year: {year_2026}")

    # Clear existing data for a clean seed
    Invoice.objects.filter(student=student).delete()
    Payment.objects.filter(student=student).delete()
    AuxiliaryCharge.objects.filter(student=student).delete()
    
    # Reset balance for clean start
    profile.fee_balance = 0
    profile.save()

    # ================================================================
    # INVOICES (Term-linked billing)
    # ================================================================
    
    # Term 1: Tuition - billed Jan 6
    inv1 = Invoice.objects.create(
        student=student,
        description="Term 1 Tuition Fees",
        amount=Decimal('45000.00'),
        academic_year=year_2026,
        term=term1,
    )
    print(f"  Invoice: {inv1.description} -> KES {inv1.amount}")

    # Term 1: Activity Levy - billed Jan 8
    inv2 = Invoice.objects.create(
        student=student,
        description="Term 1 Activity Levy",
        amount=Decimal('3500.00'),
        academic_year=year_2026,
        term=term1,
    )
    print(f"  Invoice: {inv2.description} -> KES {inv2.amount}")

    # Term 2: Tuition - billed Apr 7
    inv3 = Invoice.objects.create(
        student=student,
        description="Term 2 Tuition Fees",
        amount=Decimal('45000.00'),
        academic_year=year_2026,
        term=term2,
    )
    print(f"  Invoice: {inv3.description} -> KES {inv3.amount}")

    # Term 2: Transport - billed Apr 10
    inv4 = Invoice.objects.create(
        student=student,
        description="Term 2 Transport Levy",
        amount=Decimal('5000.00'),
        academic_year=year_2026,
        term=term2,
    )
    print(f"  Invoice: {inv4.description} -> KES {inv4.amount}")

    # ================================================================
    # PAYMENTS (Term-linked)
    # ================================================================

    # Term 1 payment 1: Bank Transfer Jan 12
    p1 = Payment.objects.create(
        student=student,
        amount=Decimal('25000.00'),
        method='Bank',
        reference='BK-JAN-9921',
        term=term1,
        date_paid=date(2026, 1, 12),
        recorded_by=recorder
    )
    print(f"  Payment: KES {p1.amount} via {p1.method} ({p1.reference}) [T1]")

    # Term 1 payment 2: M-Pesa Feb 18
    p2 = Payment.objects.create(
        student=student,
        amount=Decimal('20000.00'),
        method='Mpesa',
        reference='QKX28819JJ',
        term=term1,
        date_paid=date(2026, 2, 18),
        recorded_by=recorder
    )
    print(f"  Payment: KES {p2.amount} via {p2.method} ({p2.reference}) [T1]")

    # Term 1 payment 3: Cash clearance Mar 5
    p3 = Payment.objects.create(
        student=student,
        amount=Decimal('3500.00'),
        method='Cash',
        reference='CSH-MAR-0042',
        term=term1,
        date_paid=date(2026, 3, 5),
        recorded_by=recorder
    )
    print(f"  Payment: KES {p3.amount} via {p3.method} ({p3.reference}) [T1]")

    # Term 2 payment 1: Bank Transfer Apr 15
    p4 = Payment.objects.create(
        student=student,
        amount=Decimal('30000.00'),
        method='Bank',
        reference='BK-APR-1102',
        term=term2,
        date_paid=date(2026, 4, 15),
        recorded_by=recorder
    )
    print(f"  Payment: KES {p4.amount} via {p4.method} ({p4.reference}) [T2]")

    # ================================================================
    # AUXILIARY SERVICES (Swimming, Remedial, etc.)
    # ================================================================

    # Create service types
    swimming, _ = AuxiliaryServiceType.objects.get_or_create(
        name="Swimming Lessons",
        school=school,
        defaults={'amount': Decimal('3000.00'), 'description': 'Weekly pool sessions'}
    )

    remedial, _ = AuxiliaryServiceType.objects.get_or_create(
        name="Remedial Classes",
        school=school,
        defaults={'amount': Decimal('2000.00'), 'description': 'After-school academic support'}
    )

    # Auxiliary Charges
    ac1 = AuxiliaryCharge.objects.create(
        student=student,
        service_type=swimming,
        description="Term 1 Swimming",
        amount=Decimal('3000.00'),
        term=term1,
        academic_year=year_2026,
        created_by=recorder
    )
    print(f"  Aux Charge: {ac1.description} -> KES {ac1.amount}")

    ac2 = AuxiliaryCharge.objects.create(
        student=student,
        service_type=remedial,
        description="Term 2 Remedial Maths",
        amount=Decimal('2000.00'),
        term=term2,
        academic_year=year_2026,
        created_by=recorder
    )
    print(f"  Aux Charge: {ac2.description} -> KES {ac2.amount}")

    # Auxiliary Payments
    ap1 = AuxiliaryPayment.objects.create(
        charge=ac1,
        amount=Decimal('3000.00'),
        method='Mpesa',
        reference='MPX-SWIM-881',
        term=term1,
        date_paid=date(2026, 2, 10),
        recorded_by=recorder
    )
    print(f"  Aux Payment: KES {ap1.amount} for {ac1.description} [T1]")

    ap2 = AuxiliaryPayment.objects.create(
        charge=ac2,
        amount=Decimal('1000.00'),
        method='Cash',
        reference='CSH-REM-045',
        term=term2,
        date_paid=date(2026, 4, 18),
        recorded_by=recorder
    )
    print(f"  Aux Payment: KES {ap2.amount} for {ac2.description} [T2]")

    # ================================================================
    # SUMMARY
    # ================================================================
    profile.refresh_from_db()
    total_invoiced = Invoice.objects.filter(student=student).aggregate(
        total=django.db.models.Sum('amount'))['total'] or 0
    total_paid = Payment.objects.filter(student=student).aggregate(
        total=django.db.models.Sum('amount'))['total'] or 0

    print("\n" + "="*50)
    print(f"  Student: {student.get_full_name()}")
    print(f"  Total Invoiced: KES {total_invoiced}")
    print(f"  Total Paid: KES {total_paid}")
    print(f"  Fee Balance: KES {profile.fee_balance}")
    print(f"  Aux Charges: 2 | Aux Payments: 2")
    print("="*50)

if __name__ == "__main__":
    import django.db.models
    seed_financials()
